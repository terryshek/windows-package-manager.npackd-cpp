#ifndef APP_H
#define APP_H

#include <time.h>

#include <QtCore/QCoreApplication>
#include <qdebug.h>
#include <qstringlist.h>
#include <qstring.h>

#include "..\wpmcpp\repository.h"
#include "..\wpmcpp\commandline.h"
#include "..\wpmcpp\job.h"
#include "..\wpmcpp\clprogress.h"

/**
 * NpackdCL
 */
class App: public QObject
{
    Q_OBJECT
private:
    CommandLine cl;
    CLProgress clp;

    void addNpackdCL();

    void usage();
    int path();
    int add();
    int remove();
    int addRepo();
    int removeRepo();
    int list();
    int info();
    int update();
    int download();

    /**
     * Internal tests.
     *
     * @param argc number of arguments
     * @param argv arguments
     * @return exit code
     */
    int unitTests();

    QString reinstallTestPackage(QString rep);
public:
    /**
     * Process the command line.
     *
     * @return exit code
     */
    int process();
};

#endif // APP_H
