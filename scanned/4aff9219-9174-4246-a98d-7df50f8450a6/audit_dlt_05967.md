# [?] qt: Preventing a crash using "window" menu during application start-up

## Summary
Severity: Unknown
Chain: Bitcoin Cash
Component: bitcoin-cash-node/bitcoin-cash-node
Published: 2021-03-13
Source: https://github.com/bitcoin-cash-node/bitcoin-cash-node/commit/d836e896ecc743514a7f484f974988bd3d2e367e
Type: security-commit

## Details
qt: Preventing a crash using "window" menu during application start-up

This commit fixes a bug introduced into
459b3bb5d02a8deed9456ff9087f3c5b3e4e88e1: qt: Add Window menu Some options in
the menu are enabled while the node is initializing, and can lead to a crash if
selected by the user.

The issue was reproduced and fixed on OSX, but the problem seems
platform-independent.

**How to reproduce**

* Run BitcoinCashNode-Qt
* While the application is starting-up, go into the 'Window' menu, and select
  'Console traffic'
* The application will crash

**What this fixes**

The menu items are disabled while the application is initializing, and enabled
once the initialization is over.

**How to test**

* Run BitcoinCashNode-Qt
* While the application is starting-up, go into the 'Window' menu, see that the
  items 'Main window', 'Information', 'Console', 'Network traffic' and 'Peers'
  are disabled.
* Once the splash window vanishes, these items are enabled.

## Patch
### src/qt/bitcoingui.cpp
```diff
@@ -521,9 +521,9 @@ void BitcoinGUI::createMenuBar() {
     if (walletFrame) {
 #ifdef Q_OS_MAC
         window_menu->addSeparator();
-        QAction *main_window_action = window_menu->addAction(tr("Main Window"));
+        m_main_window_action = window_menu->addAction(tr("Main Window"));
         // No setStatusTip+setToolTip here because these don't work on the MacOS menu bar.
-        connect(main_window_action, &QAction::triggered,
+        connect(m_main_window_action, &QAction::triggered, this,
                 [this] { GUIUtil::bringToFront(this); });
 #endif
         window_menu->addSeparator();
@@ -543,17 +543,21 @@ void BitcoinGUI::createMenuBar() {
         tab_action->setStatusTip(tr("Show the %1 tab of the Node Window").arg(title));
         tab_action->setToolTip(tab_action->statusTip());
         tab_action->setShortcut(rpcConsole->tabShortcut(tab_type));
-        connect(tab_action, &QAction::triggered, [this, tab_type] {
+        connect(tab_action, &QAction::triggered, this, [this, tab_type] {
             rpcConsole->setTabFocus(tab_type);
             showDebugWindow();
         });
+
+        m_node_actions.append(tab_action);
     }
 
     QMenu *help = appMenuBar->addMenu(tr("&Help"));
     help->addAction(showHelpMessageAction);
     help->addSeparator();
     help->addAction(aboutAction);
     help->addAction(aboutQtAction);
+
+    setWindowActionsEnabled(false);
 }
 
 void BitcoinGUI::createToolBars() {
@@ -1212,6 +1216,8 @@ void BitcoinGUI::showEvent(QShowEvent *event) {
     openRPCConsoleAction->setEnabled(true);
     aboutAction->setEnabled(true);
     optionsAction->setEnabled(true);
+
+    setWindowActionsEnabled(true);
 }
 
 #ifdef ENABLE_WALLET
@@ -1435,6 +1441,16 @@ void BitcoinGUI::showModalOverlay() {
     }
 }
 
+void BitcoinGUI::setWindowActionsEnabled(bool enabled) {
+    if (m_main_window_action != nullptr) {
+        m_main_window_action->setEnabled(enabled);
+    }
+
+    for (QAction *action : m_node_actions) {
+         action->setEnabled(enabled);
+    }
+}
+
 static bool ThreadSafeMessageBox(BitcoinGUI *gui, const std::string &message,
                                  const std::string &caption,
                                  unsigned int style) {
```

### src/qt/bitcoingui.h
```diff
@@ -95,6 +95,7 @@ class BitcoinGUI : public QMainWindow {
 #endif // ENABLE_WALLET
     bool enableWallet = false;
 
+
     /** Disconnect core signals from GUI client */
     void unsubscribeFromCoreSignals();
 
@@ -150,6 +151,11 @@ class BitcoinGUI : public QMainWindow {
     QAction *m_wallet_selector_label_action = nullptr;
     QAction *m_wallet_selector_action = nullptr;
 
+    /** Only set to non-nullptr in constructor on OSX */
+    QAction *m_main_window_action = nullptr;
+
+    QVector<QAction *> m_node_actions;
+
     QLabel *m_wallet_selector_label = nullptr;
     QComboBox *m_wallet_selector = nullptr;
 
@@ -182,7 +188,10 @@ class BitcoinGUI : public QMainWindow {
     /** Enable or disable all wallet-related actions */
     void setWalletActionsEnabled(bool enabled);
 
-    /** Connect core signals to GUI client */
+    /** @brief Enable or disable all the main window-related actions */
+    void setWindowActionsEnabled(bool enabled);
+
+     /** Connect core signals to GUI client */
     void subscribeToCoreSignals();
 
     /** Update UI with latest network info from model. */
```

### src/qt/rpcconsole.cpp
```diff
@@ -1410,7 +1410,8 @@ void RPCConsole::unbanSelectedNode() {
 }
 
 void RPCConsole::clearSelectedNode() {
-    ui->peerWidget->selectionModel()->clearSelection();
+    if (ui->peerWidget->selectionModel())
+        ui->peerWidget->selectionModel()->clearSelection();
     cachedNodeids.clear();
     ui->detailWidget->hide();
     ui->peerHeading->setText(tr("Select a peer to view detailed information."));
```
