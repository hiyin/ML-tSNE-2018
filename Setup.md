# Singleton

This README would normally document whatever steps are necessary to get your application up and running.

### What is this repository for? ###

* Quick summary
* Version
* [Learn Markdown](https://bitbucket.org/tutorials/markdowndemo)




### How do I get set up? ###

* Additional dependencies to watch *
    mysqlclient (MySQLdb-python replacement) https://github.com/PyMySQL/mysqlclient-python

* Set up in local computer

    1. set up a virtual environment $VENV

    2. change to the Pyramid base directory (top-level project directory) in command line interface
       note that the secondary-level is the module directory also called singleton

    3. To download all the project dependencies run:
        $ pip install -r requirements.txt
            or
        $ pip3 install -r requirements.txt


    4. To install the singleton package run: (use sudo if required)
        $ python setup.py develop
            or
        $ python3 setup.py develop

    5. To start the server run:
       $ pserve development.ini --reload

    6. In your browser, navigate to
        localhost:6543.

* Set up in NeCTAR server

    Access to hosts is via ssh keypairs (attached in email)

    Instructions for using it can be found at: https://support.nectar.org.au/support/solutions/articles/6000055446-accessing-instances

    The Hostname and IP address for this instance: ubuntu@144.6.239.203.

    1. Download ssh keypairs file i.e. nectar_archy
    2. Change permission of the keypairs file
        $ chmod 600 nectar_archy
    3. Connect to ssh via Terminal/command-line
        $ ssh -i nectar_archy ubuntu@144.6.239.203

        Connection success information below:
        -------------------------------------------------------------------------------------
        NeCTAR  x86_64
        Image details and information is available at
        https://support.nectar.org.au/support/solutions/articles/6000106269-image-catalog
        -------------------------------------------------------------------------------------

    5. Once sshed onto VM, enter into project home directory on the server and update project (if needed)
        ubuntu@singleton$ cd src/singleton
        ubuntu@singleton$ git pull

    6. First timer to set up
       (same as to setting up in local computer)
       Specific to server VM:
        1. ubuntu@singleton:~/src/singleton$ export PATH=$PATH: ~/src/singleton/env/bin
        2. use pip3.4 to install and
        3. python3.4 to build

    7. Start server
        ubuntu@singleton:~/src/singleton$ ps auxw | grep pserve
        ubuntu@singleton:~/src/singleton$ kill PID (i.e. second column)
        ubuntu@singleton:~/src/singleton$ ./start_pyramid_server.sh
        -------------------------------------------------------------------------------------
        Starting subprocess with file monitor
        Starting server in PID 17919.
        serving on http://0.0.0.0:80
        -------------------------------------------------------------------------------------



* Working with feature branch
  Name of feature branch: singleton-your first name e.g. singleton-angela
       1. Use VCS > Git > Branches (PyCharm menu) to check out a new branch
       2. Start developing
       3. Finish developing
       4. Possibly rebase onto master, if master has moved forward since you created the branch
       5. Create a pull request to merge into master
       6. Either get the pull request approved, or if it's clear the merge won't have any bad side effects, just merge.
       7. Delete feature branch

* Configuration
* Dependencies
* Database configuration
* How to run tests
* Deployment instructions

### Contribution guidelines ###

* Writing tests
* Code review
* Other guidelines

### Who do I talk to? ###

* Repo owner or admin
* Other community or team contact

### Similar applications ###

Single cell expression analysis is a relatively new area of research with new tools coming out rapidly. Here is a list of other applications of note.

* http://www.qlucore.com/overview
* http://www.biorxiv.org/content/early/2016/03/12/043463
* https://genestack.com/
