# [?] Merge #13284: gui: fix visual "overflow" of amount input.

## Summary
Severity: Unknown
Chain: Bitcoin Cash
Component: bitcoin-cash-node/bitcoin-cash-node
Published: 2018-05-24
Source: https://github.com/bitcoin-cash-node/bitcoin-cash-node/commit/92024366650c6898b47885fb6ecfc62a0f7127c6
Type: security-commit

## Details
Merge #13284: gui: fix visual "overflow" of amount input.

Summary:
5f3cbde9de842a8d565b6580c6050310d897065b Increased max width of amount field to prevent number overflow bug. (Brandon Ruggles)

Pull request description:

  Fixes #13231.

  I was able to reproduce this bug within my own Fedora 27 VM. Following @jonasschnelli's advice, I first tried to change `setAlignment(Qt::AlignRight);` to `setAlignment(Qt::AlignLeft);`, however, I realized that this wouldn't fix the underlying overflow problem, as it would only make it easier to see the most significant digits under certain scenarios. The reason for the overflow is that Fedora uses plus and minus buttons on the Qt spin box class, rather than up and down arrows, which is what happens on **most** other operating systems. These plus and minus buttons take up more width, and therefore provide less space for text.

  The solution I went with was the second suggestion by @jonasschnelli, which was to just increase the maximum width of the amount box. After some experimentation, 240 seemed to be the smallest max width that would allow as many digits as one would want in the amount box without overflow, even with the plus and minus buttons in Fedora.

  Please let me know if there are any issues with this PR and I will work to fix them. Thank you!

Tree-SHA512: 155f34cec74af46ec1fe723a5241798d8e15607a4e1cdc493014dcc0ae9818a001c7901831168b5f26a6953ec5a992e4a67c57db1ad377bcf10f12941688ee93

Backport of Core PR13284
https://github.com/bitcoin/bitcoin/pull/13284/

Test Plan:
  make check
  bitcoin-qt -> Send -> Max out the number of characters in Amount

Reviewers: deadalnix, Fabien, jasonbcox, O1 Bitcoin ABC, #bitcoin_abc

Reviewed By: deadalnix, O1 Bitcoin ABC, #bitcoin_abc

Differential Revision: https://reviews.bitcoinabc.org/D4165

## Patch
### src/qt/bitcoinamountfield.cpp
```diff
@@ -199,7 +199,7 @@ BitcoinAmountField::BitcoinAmountField(QWidget *parent)
     amount = new AmountSpinBox(this);
     amount->setLocale(QLocale::c());
     amount->installEventFilter(this);
-    amount->setMaximumWidth(170);
+    amount->setMaximumWidth(240);
 
     QHBoxLayout *layout = new QHBoxLayout(this);
     layout->addWidget(amount);
```
