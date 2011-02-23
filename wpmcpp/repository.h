#ifndef REPOSITORY_H
#define REPOSITORY_H

#include <windows.h>

#include "qfile.h"
#include "qlist.h"
#include "qurl.h"
#include "qtemporaryfile.h"
#include "qdom.h"

#include "package.h"
#include "packageversion.h"
#include "license.h"
#include "node.h"
#include "digraph.h"

/**
 * A repository is a list of packages and package versions.
 */
class Repository
{
private:
    // TODO: this is never freed
    static Repository* def;

    Digraph* installedGraph;

    static Package* createPackage(QDomElement* e);
    static PackageVersionFile* createPackageVersionFile(QDomElement* e);
    static Dependency* createDependency(QDomElement* e);
    static License* createLicense(QDomElement* e);
    static PackageVersion* createPackageVersion(QDomElement* e);
    static DetectFile* createDetectFile(QDomElement* e);

    void loadOne(QUrl* url, Job* job);

    void addWindowsPackage();

    void clearExternallyInstalled(QString package);
    void detectOneDotNet(HKEY hk2, const QString& keyName);
    void detectMSIProducts();
    void detectDotNet();
    void detectMicrosoftInstaller();
    void detectMSXML();
    void detectJRE(bool w64bit);
    void detectJDK(bool w64bit);

    /**
     * @param exact if true, only exact matches to packages from current
     *     repositories recognized as existing software (e.g. something like
     *     com.mysoftware.MySoftware-2.2.3). This setting should help in rare
     *     cases when Npackd 1.14 and 1.15 are used in parallel for some time
     *     If the value is false, also
     *     packages not known in current repositories are recognized as
     *     installed.
     */
    void scanPre1_15Dir(bool exact);

    /**
     * All paths should be in lower case
     * and separated with \ and not / and cannot end with \.
     *
     * @param path directory
     * @param ignore ignored directories
     */
    void scan(const QString& path, Job* job, int level, QStringList& ignore);
public:
    /**
     * Package versions. All version numbers should be normalized.
     */
    QList<PackageVersion*> packageVersions;

    /**
     * Packages.
     */
    QList<Package*> packages;

    /**
     * Licenses.
     */
    QList<License*> licenses;

    /**
     * Creates an empty repository.
     */
    Repository();

    ~Repository();

    void process(Job* job, const QList<InstallOperation*> &install);

    /**
     * Adds unknown in the repository, but installed packages.
     */
    void addUnknownExistingPackages();

    /**
     * Changes the value of the system-wide NPACKD_CL variable to point to the
     * newest installed version of NpackdCL.
     */
    void updateNpackdCLEnvVar();

    /**
     * Recognizes applications installed without Npackd.
     *
     * @param job job object
     */
    void recognize(Job* job);

    /**
     * Can be called if a package version was detected.
     *
     * @param package package name
     * @param v found version
     */
    void versionDetected(const QString& package, const Version& v,
            const QString &path, const bool external);

    /**
     * Finds all installed packages. This method lists all directories in the
     * installation directory and finds the corresponding package versions
     *
     * @return the list of installed package versions (the objects should not
     *     be freed)
     */
    QList<PackageVersion*> getInstalled();

    /**
     * @return digraph with installed package versions. Each Node.userData is
     *     of type PackageVersion* and represents an installed package version.
     *     The memory should not be freed. The first object in the list has
     *     the userData==0 and represents the user which "depends" on a list
     *     of packages (uses some programs).
     */
    Digraph* getInstalledGraph();

    /**
     * This method should always be called after something was installed or
     * uninstalled so that the Repository object can re-calculate some internal
     * data.
     */
    void somethingWasInstalledOrUninstalled();

    /**
     * Counts the number of installed packages that can be updated.
     *
     * @return the number
     */
    int countUpdates();

    /**
     * Loads the content from the URLs.
     *
     * @param job job for this method
     */
    void load(Job* job);

    /**
     * Scans the hard drive for existing applications.
     *
     * @param job job for this method
     */
    void scanHardDrive(Job* job);

    /**
     * Searches for a package by name.
     *
     * @param name name of the package like "org.server.Word"
     * @return found package or 0
     */
    Package* findPackage(const QString& name);

    /**
     * Searches for a license by name.
     *
     * @param name name of the license like "org.gnu.GPLv3"
     * @return found license or 0
     */
    License* findLicense(const QString& name);

    /**
     * Find the newest available package version.
     *
     * @param name name of the package like "org.server.Word"
     * @return found package version or 0
     */
    PackageVersion* findNewestPackageVersion(const QString& name);

    /**
     * Find the newest installed package version.
     *
     * @param name name of the package like "org.server.Word"
     * @return found package version or 0
     */
    PackageVersion* findNewestInstalledPackageVersion(const QString& name);

    /**
     * Find the newest available package version.
     *
     * @param package name of the package like "org.server.Word"
     * @param version package version
     * @return found package version or 0
     */
    PackageVersion* findPackageVersion(const QString& package,
            const Version& version);

    /**
     * @return newly created object pointing to the repositories
     */
    static QList<QUrl*> getRepositoryURLs();

    /*
     * Changes the default repository url.
     *
     * @param urls new URLs
     */
    static void setRepositoryURLs(QList<QUrl*>& urls);

    /**
     * @return default repository
     */
    static Repository* getDefault();
};

#endif // REPOSITORY_H
