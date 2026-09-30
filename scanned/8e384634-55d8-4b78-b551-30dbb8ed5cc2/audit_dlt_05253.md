# [?] [bugfix] fix text overflow on paper wallet

## Summary
Severity: Unknown
Chain: Dogecoin
Component: dogecoin/dogecoin
Published: 2021-03-20
Source: https://github.com/dogecoin/dogecoin/commit/dfb78d26dc38cf86783ec0161408c593556337d6
Type: security-commit

## Details
[bugfix] fix text overflow on paper wallet

- use Courier instead of "monospace" as font family as the latter
  does not translate to an actual monospace font properly
- make address and privkey fields to have equal dimensions and
  margins, because their fontsizes are calculated uniformly too
- make the max font size 98% of the wallet, instead of 99%

## Patch
### src/qt/forms/paperwalletdialog.ui
```diff
@@ -82,14 +82,14 @@
    <property name="geometry">
     <rect>
      <x>212</x>
-     <y>20</y>
+     <y>10</y>
      <width>31</width>
-     <height>341</height>
+     <height>361</height>
     </rect>
    </property>
    <property name="font">
     <font>
-     <family>Monospace</family>
+     <family>Courier</family>
      <pointsize>12</pointsize>
      <weight>75</weight>
      <italic>false</italic>
@@ -117,7 +117,7 @@
    </property>
    <property name="font">
     <font>
-     <family>Monospace</family>
+     <family>Courier</family>
      <pointsize>8</pointsize>
      <weight>50</weight>
      <italic>false</italic>
```

### src/qt/utilitydialog.cpp
```diff
@@ -200,7 +200,7 @@ PaperWalletDialog::PaperWalletDialog(QWidget *parent) :
     ui->buttonBox->addButton(tr("Close"), QDialogButtonBox::RejectRole);
 
     // Begin with a small bold monospace font for the textual version of the key and address.
-    QFont font("Monospace");
+    QFont font("Courier");
     font.setBold(true);
     font.setStyleHint(QFont::TypeWriter);
     font.setPixelSize(1);
@@ -302,7 +302,7 @@ void PaperWalletDialog::on_getNewAddress_clicked()
     // Update the fonts to fit the height of the wallet.
     // This should only really trigger the first time since the font size persists.
     double paperHeight = (double)ui->paperTemplate->height();
-    double maxTextWidth = paperHeight * 0.99;
+    double maxTextWidth = paperHeight * 0.98;
     double minTextWidth = paperHeight * 0.95;
     int pixelSizeStep = 1;
 
```
