##############################################################################
# Copyright (c) 2013-2017, Lawrence Livermore National Security, LLC.
# Produced at the Lawrence Livermore National Laboratory.
#
# This file is part of Spack.
# Created by Todd Gamblin, tgamblin@llnl.gov, All rights reserved.
# LLNL-CODE-647188
#
# For details, see https://github.com/llnl/spack
# Please also see the NOTICE and LICENSE files for our notice and the LGPL.
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License (as
# published by the Free Software Foundation) version 2.1, February 1999.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the IMPLIED WARRANTY OF
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the terms and
# conditions of the GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307 USA
##############################################################################
from spack import *
import os
import sys


class Sundials(CMakePackage):
    """SUNDIALS (SUite of Nonlinear and DIfferential/ALgebraic equation
    Solvers)"""

    homepage = "https://computation.llnl.gov/projects/sundials"
    url = "https://computation.llnl.gov/projects/sundials/download/sundials-2.7.0.tar.gz"
    maintainers = ['cswoodward', 'gardner48']

    # ==========================================================================
    # Versions
    # ==========================================================================

    version('3.0.0-beta-2',
            git='https://github.com/LLNL/sundials.git', tag='v3.0.0-beta-2')
    version('2.7.0', 'c304631b9bc82877d7b0e9f4d4fd94d3', preferred=True)
    version('2.6.2', '3deeb0ede9f514184c6bd83ecab77d95')

    # ==========================================================================
    # Variants
    # ==========================================================================

    # SUNDIALS solvers
    sun_solvers = ['CVODE', 'CVODES', 'ARKODE', 'IDA', 'IDAS', 'KINSOL']

    for pkg in sun_solvers:
        variant(pkg, default=True,
                description='Enable %s solver' % pkg)

    # Real type
    variant(
        'precision',
        default='double',
        description='real type precision',
        values=('single', 'double', 'extended'),
        multi=False
    )

    # Index type
    # NOTE: Default to True until v3.0.0 is final as only 64bit integers are
    # supported before v3.0.0.
    variant('int64', default=True,
            description='Use 64bit integers for indices')

    # Parallelism
    variant('mpi',     default=True,
            description='Enable MPI parallel vector')
    variant('openmp',  default=False,
            description='Enable OpenMP parallel vector')
    variant('pthread', default=False,
            description='Enable Pthreads parallel vector')
    variant('cuda',    default=False,
            description='Enable CUDA parallel vector')
    variant('raja',    default=False,
            description='Enable RAJA parallel vector')

    # External libraries
    variant('lapack',     default=False,
            description='Enable LAPACK direct solvers')
    variant('klu',        default=False,
            description='Enable KLU sparse, direct solver')
    variant('superlu-mt', default=False,
            description='Enable SuperLU_MT sparse, direct solver')
    variant('hypre',      default=False,
            description='Enable Hypre MPI parallel vector')
    variant('petsc',      default=False,
            description='Enable PETSc MPI parallel vector')

    # Library type
    variant('shared', default=True,
            description='Build shared libraries')
    variant('static', default=True,
            description='Build static libraries')

    # Fortran interface
    variant('fcmix', default=False,
            description='Enable Fortran interface')

    # Examples
    variant('examples-c',       default=True,
            description='Enable C examples')
    variant('examples-cxx',     default=False,
            description='Enable C++ examples')
    variant('examples-f77',     default=True,
            description='Enable Fortran 77 examples')
    variant('examples-f90',     default=False,
            description='Enable Fortran 90 examples')
    variant('examples-cuda',    default=False,
            description='Enable CUDA examples')
    variant('examples-raja',    default=False,
            description='Enable RAJA examples')
    variant('examples-install', default=True,
            description='Install examples')

    # Generic (std-c) math libraries (UNIX only)
    variant('generic-math', default=True,
            description='Use generic (std-c) math libraries on unix systems')

    # ==========================================================================
    # Conflicts
    # ==========================================================================

    # Options added after v2.6.2
    conflicts('+hypre', when='@:2.6.2')
    conflicts('+petsc', when='@:2.6.2')

    # Options added after v2.7.0
    conflicts('+cuda',          when='@:2.7.0')
    conflicts('+raja',          when='@:2.7.0')
    conflicts('~int64',         when='@:2.7.0')
    conflicts('+examples-cuda', when='@:2.7.0')
    conflicts('+examples-raja', when='@:2.7.0')

    # External libraries incompatible with 64-bit indices
    conflicts('+lapack', when='@3.0.0-beta-2: +int64')
    conflicts('+hypre',  when='+hypre@:2.6.1a +int64')

    # External libraries incompatible with single precision
    conflicts('+klu',   when='precision=single')
    conflicts('+hypre', when='+hypre@:2.12.0 precision=single')

    # External libraries incompatible with extended (quad) precision
    conflicts('+lapack',     when='precision=extended')
    conflicts('+superlu-mt', when='precision=extended')
    conflicts('+klu',        when='precision=extended')
    conflicts('+hypre',      when='+hypre@:2.12.0 precision=extended')

    # External libraries that need to be built with MPI
    conflicts('+hypre', when='~mpi')
    conflicts('+petsc', when='~mpi')

    # SuperLU_MT interface requires lapack for external blas (before v3.0.0)
    conflicts('+superlu-mt', when='@:2.7.0 ~lapack')

    # ==========================================================================
    # Dependencies
    # ==========================================================================

    # Build dependencies
    depends_on('cmake@2.8.1:', type='build')

    # MPI related dependencies
    depends_on('mpi', when='+mpi')
    depends_on('mpi', when='+hypre')
    depends_on('mpi', when='+petsc')

    # Other parallelism dependencies
    depends_on('cuda', when='+cuda')
    depends_on('raja', when='+raja')

    # External libraries
    depends_on('blas',         when='+lapack')
    depends_on('lapack',       when='+lapack')
    depends_on('suite-sparse', when='+klu')

    # Require that external libraries built with the same precision
    depends_on('petsc~double', when='+petsc precision=single')
    depends_on('petsc+double', when='+petsc precision=double')

    # Require that external libraries built with the same index type
    depends_on('hypre~int64', when='+hypre ~int64')
    depends_on('hypre+int64', when='+hypre +int64')
    depends_on('petsc~int64', when='+petsc ~int64')
    depends_on('petsc+int64', when='+petsc +int64')

    # Require that PETSc is built with MPI
    depends_on('petsc+mpi', when='+petsc')

    # Require that SuperLU_MT built with external blas
    depends_on('superlu-mt+blas', when='+superlu-mt')

    # ==========================================================================
    # SUNDIALS Settings
    # ==========================================================================

    def cmake_args(self):
        spec = self.spec

        def on_off(varstr):
            return 'ON' if varstr in self.spec else 'OFF'

        fortran_flag = self.compiler.pic_flag
        if spec.satisfies('%clang platform=darwin'):
            mpif77 = Executable(self.spec['mpi'].mpif77)
            libgfortran = LibraryList(mpif77('--print-file-name',
                                             'libgfortran.a', output=str))
            fortran_flag += ' ' + libgfortran.ld_flags

        # List of CMake arguments
        # Note: CMAKE_INSTALL_PREFIX and CMAKE_BUILD_TYPE are set automatically
        args = []

        # SUNDIALS solvers
        for pkg in self.sun_solvers:
            args.extend(['-DBUILD_%s=%s' % (pkg, on_off('+' + pkg))])

        # precision
        args.extend([
            '-DSUNDIALS_PRECISION=%s' % spec.variants['precision'].value
        ])

        # index type (after v2.7.0)
        if not spec.satisfies('@:2.7.0'):
            if '+int64' in spec:
                args.extend(['-DSUNDIALS_INDEX_TYPE=int64_t'])
            else:
                args.extend(['-DSUNDIALS_INDEX_TYPE=int32_t'])

        # Fortran interface
        args.extend(['-DFCMIX_ENABLE=%s' % on_off('+fcmix')])

        # library type
        args.extend([
            '-DBUILD_SHARED_LIBS=%s' % on_off('+shared'),
            '-DBUILD_STATIC_LIBS=%s' % on_off('+static')
        ])

        # generic (std-c) math libraries
        args.extend([
            '-DUSE_GENERIC_MATH=%s' % on_off('+generic-math')
        ])

        # parallelism
        args.extend([
            '-DMPI_ENABLE=%s'     % on_off('+mpi'),
            '-DOPENMP_ENABLE=%s'  % on_off('+openmp'),
            '-DPTHREAD_ENABLE=%s' % on_off('+pthread'),
            '-DCUDA_ENABLE=%s'    % on_off('+cuda'),
            '-DRAJA_ENABLE=%s'    % on_off('+raja')
        ])

        # MPI support
        if '+mpi' in spec:
            args.extend(['-DMPI_MPICC=%s' % spec['mpi'].mpicc])
            if 'examples-cxx' in spec:
                args.extend(['-DMPI_MPICXX=%s' % spec['mpi'].mpicxx])
            if ('+fcmix' in spec) and ('+examples-f77' in spec):
                args.extend(['-DMPI_MPIF77=%s' % spec['mpi'].mpif77])
            if ('+fcmix' in spec) and ('+examples-f90' in spec):
                args.extend(['-DMPI_MPIF90=%s' % spec['mpi'].mpifc])

        # Building with LAPACK and BLAS
        if '+lapack' in spec:
            args.extend([
                '-DLAPACK_ENABLE=ON',
                '-DLAPACK_LIBRARIES=%s'
                % (spec['lapack'].libs + spec['blas'].libs).joined(';')
            ])

        # Building with KLU
        if '+klu' in spec:
            args.extend([
                '-DKLU_ENABLE=ON',
                '-DKLU_INCLUDE_DIR=%s' % spec['suite-sparse'].prefix.include,
                '-DKLU_LIBRARY_DIR=%s' % spec['suite-sparse'].prefix.lib
            ])

        # Building with SuperLU_MT
        if '+superlu-mt' in spec:
            if not spec.satisfies('@:2.7.0'):
                args.extend([
                    '-DBLAS_ENABLE=ON',
                    '-DBLAS_LIBRARIES=%s' % spec['blas'].libs
                ])
            args.extend([
                '-DSUPERLUMT_ENABLE=ON',
                '-DSUPERLUMT_INCLUDE_DIR=%s'
                % spec['superlu-mt'].prefix.include,
                '-DSUPERLUMT_LIBRARY_DIR=%s'
                % spec['superlu-mt'].prefix.lib
            ])
            if spec.satisfies('^superlu-mt+openmp'):
                args.append('-DSUPERLUMT_THREAD_TYPE=OpenMP')
            else:
                args.append('-DSUPERLUMT_THREAD_TYPE=Pthread')

        # Building with Hypre
        if '+hypre' in spec:
            args.extend([
                '-DHYPRE_ENABLE=ON',
                '-DHYPRE_INCLUDE_DIR=%s' % spec['hypre'].prefix.include,
                '-DHYPRE_LIBRARY_DIR=%s' % spec['hypre'].prefix.lib
            ])

        # Building with PETSc
        if '+petsc' in spec:
            args.extend([
                '-DPETSC_ENABLE=ON',
                '-DPETSC_INCLUDE_DIR=%s' % spec['petsc'].prefix.include,
                '-DPETSC_LIBRARY_DIR=%s' % spec['petsc'].prefix.lib
            ])

        # Examples
        if not spec.satisfies('@:2.7.0'):
            args.extend([
                '-DEXAMPLES_ENABLE_C=%s'    % on_off('+examples-c'),
                '-DEXAMPLES_ENABLE_CXX=%s'  % on_off('+examples-cxx'),
                '-DEXAMPLES_ENABLE_F77=%s'  % on_off('+examples-f77'),
                '-DEXAMPLES_ENABLE_F90=%s'  % on_off('+examples-f90'),
                '-DEXAMPLES_ENABLE_CUDA=%s' % on_off('+examples-cuda'),
                '-DEXAMPLES_ENABLE_RAJA=%s' % on_off('+examples-raja')
            ])
        else:
            args.extend([
                '-DEXAMPLES_ENABLE=%s' % on_off('+examples-c'),
                '-DCXX_ENABLE=%s'      % on_off('+examples-cxx'),
                '-DF90_ENABLE=%s'      % on_off('+examples-f90')
            ])

        args.extend([
            '-DEXAMPLES_INSTALL=%s' % on_off('+examples-install')
        ])

        return args

    # ==========================================================================
    # Post Install Actions
    # ==========================================================================

    @run_after('install')
    def post_install(self):
        """Run after install to fix install name of dynamic libraries
        on Darwin to have full path and install the LICENSE file."""
        prefix = self.spec.prefix

        if (sys.platform == 'darwin'):
            fix_darwin_install_name(prefix.lib)

        install('LICENSE', prefix)

    @run_after('install')
    def filter_compilers(self):
        """Run after install to tell the example program Makefiles
        to use the compilers that Spack built the package with.

        If this isn't done, they'll have CC, CPP, and F77 set to
        Spack's generic cc and f77. We want them to be bound to
        whatever compiler they were built with."""

        kwargs = {'ignore_absent': True, 'backup': False, 'string': True}
        dirname = os.path.join(self.prefix, 'examples')

        cc_files = [
            'arkode/C_openmp/Makefile',
            'arkode/C_parallel/Makefile',
            'arkode/C_parhyp/Makefile',
            'arkode/C_serial/Makefile',
            'cvode/C_openmp/Makefile',
            'cvode/parallel/Makefile',
            'cvode/parhyp/Makefile',
            'cvode/serial/Makefile',
            'cvodes/C_openmp/Makefile',
            'cvodes/parallel/Makefile',
            'cvodes/serial/Makefile',
            'ida/C_openmp/Makefile',
            'ida/parallel/Makefile',
            'ida/petsc/Makefile',
            'ida/serial/Makefile',
            'idas/C_openmp/Makefile',
            'idas/parallel/Makefile',
            'idas/serial/Makefile',
            'kinsol/C_openmp/Makefile',
            'kinsol/parallel/Makefile',
            'kinsol/serial/Makefile',
            'nvector/C_openmp/Makefile',
            'nvector/parallel/Makefile',
            'nvector/parhyp/Makefile',
            'nvector/petsc/Makefile',
            'nvector/pthreads/Makefile',
            'nvector/serial/Makefile',
            'sunlinsol/band/Makefile',
            'sunlinsol/dense/Makefile',
            'sunlinsol/klu/Makefile',
            'sunlinsol/lapackband/Makefile',
            'sunlinsol/lapackdense/Makefile',
            'sunlinsol/pcg/parallel/Makefile',
            'sunlinsol/pcg/serial/Makefile',
            'sunlinsol/spbcgs/parallel/Makefile',
            'sunlinsol/spbcgs/serial/Makefile',
            'sunlinsol/spfgmr/parallel/Makefile',
            'sunlinsol/spfgmr/serial/Makefile',
            'sunlinsol/spgmr/parallel/Makefile',
            'sunlinsol/spgmr/serial/Makefile',
            'sunlinsol/sptfqmr/parallel/Makefile',
            'sunlinsol/sptfqmr/serial/Makefile',
            'sunlinsol/superlumt/Makefile',
            'sunmatrix/band/Makefile',
            'sunmatrix/dense/Makefile',
            'sunmatrix/sparse/Makefile'
        ]

        cxx_files = [
            'arkode/CXX_parallel/Makefile',
            'arkode/CXX_serial/Makefile'
            'cvode/cuda/Makefile',
            'cvode/raja/Makefile',
            'nvector/cuda/Makefile',
            'nvector/raja/Makefile'
        ]

        f77_files = [
            'arkode/F77_parallel/Makefile',
            'arkode/F77_serial/Makefile',
            'cvode/fcmix_parallel/Makefile',
            'cvode/fcmix_serial/Makefile',
            'ida/fcmix_openmp/Makefile',
            'ida/fcmix_parallel/Makefile',
            'ida/fcmix_pthreads/Makefile',
            'ida/fcmix_serial/Makefile',
            'kinsol/fcmix_parallel/Makefile',
            'kinsol/fcmix_serial/Makefile'
        ]

        f90_files = [
            'arkode/F90_parallel/Makefile',
            'arkode/F90_serial/Makefile'
        ]

        for filename in cc_files:
            filter_file(os.environ['CC'], self.compiler.cc,
                        os.path.join(dirname, filename), **kwargs)

        for filename in cc_files:
            filter_file(r'^CPP\s*=.*', self.compiler.cc,
                        os.path.join(dirname, filename), **kwargs)

        for filename in cxx_files:
            filter_file(os.environ['CXX'], self.compiler.cxx,
                        os.path.join(dirname, filename), **kwargs)

        for filename in cxx_files:
            filter_file(r'^CPP\s*=.*', self.compiler.cc,
                        os.path.join(dirname, filename), **kwargs)

        for filename in f77_files:
            filter_file(os.environ['F77'], self.compiler.f77,
                        os.path.join(dirname, filename), **kwargs)

        for filename in f90_files:
            filter_file(os.environ['FC'], self.compiler.fc,
                        os.path.join(dirname, filename), **kwargs)
