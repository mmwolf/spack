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
import distutils.dir_util


class Mrtrix3(Package):
    """MRtrix provides a set of tools to perform various advanced diffusion MRI
       analyses, including constrained spherical deconvolution (CSD),
       probabilistic tractography, track-density imaging, and apparent fibre
       density."""

    homepage = "http://www.mrtrix.org/"
    url      = "https://github.com/MRtrix3/mrtrix3"

    version('2017-09-25', commit='72aca89e3d38c9d9e0c47104d0fb5bd2cbdb536d',
            git='https://github.com/MRtrix3/mrtrix3.git')

    depends_on('python@2.7:', type=('build', 'run'))
    depends_on('py-numpy', type=('build', 'run'))
    depends_on('mesa-glu')
    depends_on('qt+opengl@4.7:')
    depends_on('eigen')
    depends_on('zlib')
    depends_on('libtiff')
    depends_on('fftw')

    conflicts('%gcc@7:', when='@2017-09-25')  # MRtrix3/mrtrix3#1041

    def install(self, spec, prefix):
        configure = Executable('./configure')
        build = Executable('./build')
        configure()
        build()
        # install_tree('.', prefix) does not work since the prefix
        # directory already exists by this point
        distutils.dir_util.copy_tree('.', prefix)

    def setup_environment(self, spac_env, run_env):
        run_env.prepend_path('PATH', self.prefix)
