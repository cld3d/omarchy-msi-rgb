# Maintainer: cld3d
pkgname=omarchy-msi-rgb
pkgver=0.1.0
pkgrel=1
pkgdesc="Theme-reactive per-key RGB control for MSI Raider laptops with SteelSeries controllers"
arch=('any')
url="https://github.com/cld3d/omarchy-msi-rgb"
license=('MIT')
depends=('python' 'hidapi')
source=("git+https://github.com/cld3d/omarchy-msi-rgb.git")
sha256sums=('SKIP')
install=omarchy-msi-rgb.install

package() {
    cd "$srcdir/$pkgname"
    make DESTDIR="$pkgdir" install
}
