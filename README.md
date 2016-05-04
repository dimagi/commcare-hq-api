# CommCare Integration Tests
Tests integration between CommCare mobile and server products

### Setup

+ `submodule update --init`
+ install `calabash-android` and `androidviewclient`
+ Copy `auth.conf.template` to `auth.conf`with the appropriate login info


### Running

+ Build the CommCare apk (or setup the keystore correctly and download a build from jenkins)
+ `./run_mobile_tests`
+ wait some unspecified amount of time
+ `./run_server_tests`


### Adding tests

+ ...
