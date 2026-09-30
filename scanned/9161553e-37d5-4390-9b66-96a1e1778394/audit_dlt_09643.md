# [?] merge bitcoin#24498: Avoid crash on startup if int specified in settings.json

## Summary
Severity: Unknown
Chain: Dash
Component: dashpay/dash
Published: 2025-01-26
Source: https://github.com/dashpay/dash/commit/f9b761401573333313f1836a4634b607fd2baa77
Type: security-commit

## Details
merge bitcoin#24498: Avoid crash on startup if int specified in settings.json

## Patch
### src/Makefile.qttest.include
```diff
@@ -8,6 +8,7 @@ TESTS += qt/test/test_dash-qt
 
 TEST_QT_MOC_CPP = \
   qt/test/moc_apptests.cpp \
+  qt/test/moc_optiontests.cpp \
   qt/test/moc_rpcnestedtests.cpp \
   qt/test/moc_trafficgraphdatatests.cpp \
   qt/test/moc_uritests.cpp
@@ -21,6 +22,7 @@ endif # ENABLE_WALLET
 TEST_QT_H = \
   qt/test/addressbooktests.h \
   qt/test/apptests.h \
+  qt/test/optiontests.h \
   qt/test/rpcnestedtests.h \
   qt/test/uritests.h \
   qt/test/util.h \
@@ -32,6 +34,7 @@ qt_test_test_dash_qt_CPPFLAGS = $(AM_CPPFLAGS) $(BITCOIN_INCLUDES) $(BITCOIN_QT_
 
 qt_test_test_dash_qt_SOURCES = \
   qt/test/apptests.cpp \
+  qt/test/optiontests.cpp \
   qt/test/rpcnestedtests.cpp \
   qt/test/test_main.cpp \
   qt/test/trafficgraphdatatests.cpp \
```

### src/qt/test/optiontests.cpp
```diff
@@ -0,0 +1,31 @@
+// Copyright (c) 2018 The Bitcoin Core developers
+// Distributed under the MIT software license, see the accompanying
+// file COPYING or http://www.opensource.org/licenses/mit-license.php.
+
+#include <qt/bitcoin.h>
+#include <qt/test/optiontests.h>
+#include <test/util/setup_common.h>
+#include <util/system.h>
+
+#include <QSettings>
+#include <QTest>
+
+#include <univalue.h>
+
+//! Entry point for BitcoinApplication tests.
+void OptionTests::optionTests()
+{
+    // Test regression https://github.com/bitcoin/bitcoin/issues/24457. Ensure
+    // that setting integer prune value doesn't cause an exception to be thrown
+    // in the OptionsModel constructor
+    gArgs.LockSettings([&](util::Settings& settings) {
+        settings.forced_settings.erase("prune");
+        settings.rw_settings["prune"] = 3814;
+    });
+    gArgs.WriteSettingsFile();
+    OptionsModel{};
+    gArgs.LockSettings([&](util::Settings& settings) {
+        settings.rw_settings.erase("prune");
+    });
+    gArgs.WriteSettingsFile();
+}
```

### src/qt/test/optiontests.h
```diff
@@ -0,0 +1,25 @@
+// Copyright (c) 2019 The Bitcoin Core developers
+// Distributed under the MIT software license, see the accompanying
+// file COPYING or http://www.opensource.org/licenses/mit-license.php.
+
+#ifndef BITCOIN_QT_TEST_OPTIONTESTS_H
+#define BITCOIN_QT_TEST_OPTIONTESTS_H
+
+#include <qt/optionsmodel.h>
+
+#include <QObject>
+
+class OptionTests : public QObject
+{
+    Q_OBJECT
+public:
+    explicit OptionTests(interfaces::Node& node) : m_node(node) {}
+
+private Q_SLOTS:
+    void optionTests();
+
+private:
+    interfaces::Node& m_node;
+};
+
+#endif // BITCOIN_QT_TEST_OPTIONTESTS_H
```

### src/qt/test/test_main.cpp
```diff
@@ -10,6 +10,7 @@
 #include <interfaces/node.h>
 #include <qt/bitcoin.h>
 #include <qt/test/apptests.h>
+#include <qt/test/optiontests.h>
 #include <qt/test/rpcnestedtests.h>
 #include <qt/test/uritests.h>
 #include <qt/test/trafficgraphdatatests.h>
@@ -86,6 +87,10 @@ int main(int argc, char* argv[])
     if (QTest::qExec(&app_tests) != 0) {
         fInvalid = true;
     }
+    OptionTests options_tests(app.node());
+    if (QTest::qExec(&options_tests) != 0) {
+        fInvalid = true;
+    }
     URITests test1;
     if (QTest::qExec(&test1) != 0) {
         fInvalid = true;
```

### src/test/getarg_tests.cpp
```diff
@@ -3,6 +3,8 @@
 // file COPYING or http://www.opensource.org/licenses/mit-license.php.
 
 #include <test/util/setup_common.h>
+#include <univalue.h>
+#include <util/settings.h>
 #include <util/strencodings.h>
 #include <util/system.h>
 
@@ -41,6 +43,116 @@ void SetupArgs(ArgsManager& local_args, const std::vector<std::pair<std::string,
     }
 }
 
+// Test behavior of GetArg functions when string, integer, and boolean types
+// are specified in the settings.json file. GetArg functions are convenience
+// functions. The GetSetting method can always be used instead of GetArg
+// methods to retrieve original values, and there's not always an objective
+// answer to what GetArg behavior is best in every case. This test makes sure
+// there's test coverage for whatever the current behavior is, so it's not
+// broken or changed unintentionally.
+BOOST_AUTO_TEST_CASE(setting_args)
+{
+    ArgsManager args;
+    SetupArgs(args, {{"-foo", ArgsManager::ALLOW_ANY}});
+
+    auto set_foo = [&](const util::SettingsValue& value) {
+      args.LockSettings([&](util::Settings& settings) {
+        settings.rw_settings["foo"] = value;
+      });
+    };
+
+    set_foo("str");
+    BOOST_CHECK_EQUAL(args.GetSetting("foo").write(), "\"str\"");
+    BOOST_CHECK_EQUAL(args.GetArg("foo", "default"), "str");
+    BOOST_CHECK_EQUAL(args.GetArg("foo", 100), 0);
+    BOOST_CHECK_EQUAL(args.GetBoolArg("foo", true), false);
+    BOOST_CHECK_EQUAL(args.GetBoolArg("foo", false), false);
+
+    set_foo("99");
+    BOOST_CHECK_EQUAL(args.GetSetting("foo").write(), "\"99\"");
+    BOOST_CHECK_EQUAL(args.GetArg("foo", "default"), "99");
+    BOOST_CHECK_EQUAL(args.GetArg("foo", 100), 99);
+    BOOST_CHECK_EQUAL(args.GetBoolArg("foo", true), true);
+    BOOST_CHECK_EQUAL(args.GetBoolArg("foo", false), true);
+
+    set_foo("3.25");
+    BOOST_CHECK_EQUAL(args.GetSetting("foo").write(), "\"3.25\"");
+    BOOST_CHECK_EQUAL(args.GetArg("foo", "default"), "3.25");
+    BOOST_CHECK_EQUAL(args.GetArg("foo", 100), 3);
+    BOOST_CHECK_EQUAL(args.GetBoolArg("foo", true), true);
+    BOOST_CHECK_EQUAL(args.GetBoolArg("foo", false), true);
+
+    set_foo("0");
+    BOOST_CHECK_EQUAL(args.GetSetting("foo").write(), "\"0\"");
+    BOOST_CHECK_EQUAL(args.GetArg("foo", "default"), "0");
+    BOOST_CHECK_EQUAL(args.GetArg("foo", 100), 0);
+    BOOST_CHECK_EQUAL(args.GetBoolArg("foo", true), false);
+    BOOST_CHECK_EQUAL(args.GetBoolArg("foo", false), false);
+
+    set_foo("");
+    BOOST_CHECK_EQUAL(args.GetSetting("foo").write(), "\"\"");
+    BOOST_CHECK_EQUAL(args.GetArg("foo", "default"), "");
+    BOOST_CHECK_EQUAL(args.GetArg("foo", 100), 0);
+    BOOST_CHECK_EQUAL(args.GetBoolArg("foo", true), true);
+    BOOST_CHECK_EQUAL(args.GetBoolArg("foo", false), true);
+
+    set_foo(99);
+    BOOST_CHECK_EQUAL(args.GetSetting("foo").write(), "99");
+    BOOST_CHECK_EQUAL(args.GetArg("foo", "default"), "99");
+    BOOST_CHECK_EQUAL(args.GetArg("foo", 100), 99);
+    BOOST_CHECK_THROW(args.GetBoolArg("foo", true), std::runtime_error);
+    BOOST_CHECK_THROW(args.GetBoolArg("foo", false), std::runtime_error);
+
+    set_foo(3.25);
+    BOOST_CHECK_EQUAL(args.GetSetting("foo").write(), "3.25");
+    BOOST_CHECK_EQUAL(args.GetArg("foo", "default"), "3.25");
+    BOOST_CHECK_THROW(args.GetArg("foo", 100), std::runtime_error);
+    BOOST_CHECK_THROW(args.GetBoolArg("foo", true), std::runtime_error);
+    BOOST_CHECK_THROW(args.GetBoolArg("foo", false), std::runtime_error);
+
+    set_foo(0);
+    BOOST_CHECK_EQUAL(args.GetSetting("foo").write(), "0");
+    BOOST_CHECK_EQUAL(args.GetArg("foo", "default"), "0");
+    BOOST_CHECK_EQUAL(args.GetArg("foo", 100), 0);
+    BOOST_CHECK_THROW(args.GetBoolArg("foo", true), std::runtime_error);
+    BOOST_CHECK_THROW(args.GetBoolArg("foo", false), std::runtime_error);
+
+    set_foo(true);
+    BOOST_CHECK_EQUAL(args.GetSetting("foo").write(), "true");
+    BOOST_CHECK_EQUAL(args.GetArg("foo", "default"), "1");
+    BOOST_CHECK_EQUAL(args.GetArg("foo", 100), 1);
+    BOOST_CHECK_EQUAL(args.GetBoolArg("foo", true), true);
+    BOOST_CHECK_EQUAL(args.GetBoolArg("foo", false), true);
+
+    set_foo(false);
+    BOOST_CHECK_EQUAL(args.GetSetting("foo").write(), "false");
+    BOOST_CHECK_EQUAL(args.GetArg("foo", "default"), "0");
+    BOOST_CHECK_EQUAL(args.GetArg("foo", 100), 0);
+    BOOST_CHECK_EQUAL(args.GetBoolArg("foo", true), false);
+    BOOST_CHECK_EQUAL(args.GetBoolArg("foo", false), false);
+
+    set_foo(UniValue::VOBJ);
+    BOOST_CHECK_EQUAL(args.GetSetting("foo").write(), "{}");
+    BOOST_CHECK_THROW(args.GetArg("foo", "default"), std::runtime_error);
+    BOOST_CHECK_THROW(args.GetArg("foo", 100), std::runtime_error);
+    BOOST_CHECK_THROW(args.GetBoolArg("foo", true), std::runtime_error);
+    BOOST_CHECK_THROW(args.GetBoolArg("foo", false), std::runtime_error);
+
+    set_foo(UniValue::VARR);
+    BOOST_CHECK_EQUAL(args.GetSetting("foo").write(), "[]");
+    BOOST_CHECK_THROW(args.GetArg("foo", "default"), std::runtime_error);
+    BOOST_CHECK_THROW(args.GetArg("foo", 100), std::runtime_error);
+    BOOST_CHECK_THROW(args.GetBoolArg("foo", true), std::runtime_error);
+    BOOST_CHECK_THROW(args.GetBoolArg("foo", false), std::runtime_error);
+
+    set_foo(UniValue::VNULL);
+    BOOST_CHECK_EQUAL(args.GetSetting("foo").write(), "null");
+    BOOST_CHECK_EQUAL(args.GetArg("foo", "default"), "default");
+    BOOST_CHECK_EQUAL(args.GetArg("foo", 100), 100);
+    BOOST_CHECK_EQUAL(args.GetBoolArg("foo", true), true);
+    BOOST_CHECK_EQUAL(args.GetBoolArg("foo", false), false);
+}
+
 BOOST_AUTO_TEST_CASE(boolarg)
 {
     ArgsManager local_args;
```

### src/util/system.cpp
```diff
@@ -627,7 +627,7 @@ bool ArgsManager::IsArgNegated(const std::string& strArg) const
 std::string ArgsManager::GetArg(const std::string& strArg, const std::string& strDefault) const
 {
     const util::SettingsValue value = GetSetting(strArg);
-    return value.isNull() ? strDefault : value.isFalse() ? "0" : value.isTrue() ? "1" : value.get_str();
+    return value.isNull() ? strDefault : value.isFalse() ? "0" : value.isTrue() ? "1" : value.isNum() ? value.getValStr() : value.get_str();
 }
 
 int64_t ArgsManager::GetArg(const std::string& strArg, int64_t nDefault) const
```
