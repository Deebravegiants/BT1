### Title
Webhook signature only covers the raw body, not `topic`/`shop-domain` — header spoofing lets one signed payload be redirected to any registered handler or attributed to any shop - (File: `lib/shopify_api/webhooks/registry.rb`, `lib/shopify_api/webhooks/request.rb`, `lib/shopify_api/utils/hmac_validator.rb`)

### Summary
`Webhooks::Registry.process` decides which handler to invoke using `request.topic` and passes `request.shop` straight to the handler, but `Utils::HmacValidator.validate` only authenticates `request.to_signable_string`, which is defined as `@raw_body` alone. Because the `x-shopify-topic` and `x-shopify-shop-domain` headers are never part of the signed material, an attacker who obtains one legitimately-signed webhook body can replay it with those headers changed, and the HMAC check still passes.

### Finding Description
The broken binding is:

`HmacValidator.validate(request) == true` should imply `(topic, shop, body)` as a whole were authenticated by Shopify, but in fact it only proves `body` was authenticated.

Concretely:
- `Request#to_signable_string` returns `@raw_body` only: [1](#0-0) 
- `Request#topic` and `Request#shop` are read straight from attacker-controlled HTTP headers with no cryptographic binding to the body: [2](#0-1) 
- `HmacValidator.validate_signature` computes the HMAC only over `to_signable_string` (i.e. the body) and compares it to the received `hmac`: [3](#0-2) 
- `Registry.process` uses the unsigned `request.topic` to select the handler, and forwards the unsigned `request.shop` into `WebhookMetadata` that the handler acts on, immediately after the (body-only) HMAC check: [4](#0-3) 

Exploit flow: an unprivileged attacker creates their own development shop, installs the target app, and lets it register webhooks. Shopify delivers a real webhook to the app's endpoint with a valid HMAC over some JSON body (e.g. a `products/update` payload for the attacker's own store). The attacker (who runs their own server / is a MITM-free network client hitting the app endpoint directly, or captures their own callback) replays that exact same `raw_body` + `hmac` to the app endpoint again, but with:
- `x-shopify-topic` changed to a different topic that has a registered handler in this app (e.g. `customers/data_request`, `shop/redact`, or any handler doing privileged work), and/or
- `x-shopify-shop-domain` changed to the victim merchant's `*.myshopify.com` domain.

`HmacValidator.validate` recomputes the HMAC over the unchanged `raw_body` and it still matches, so `Registry.process` proceeds to call `@registry[<attacker-chosen topic>].handler.handle(...)` with `shop: <attacker-chosen shop>`. Note that `process` also does not exclude the `MANDATORY_TOPICS` set (`shop/redact`, `customers/redact`, `customers/data_request`) the way `register` does, so any handler registered for those topics (common in real apps for GDPR compliance) is reachable this way too.

None of the existing guards catch this: `HmacValidator.validate` only checks the body signature and succeeds by construction; there is no `ShopValidator.sanitize!` or any shop/topic cross-check anywhere in the webhook processing path (confirmed by searching the codebase — `ShopValidator` is only used in OAuth/token-exchange flows, never in `Webhooks::Registry` or `Webhooks::Request`); Sorbet typing only enforces that `topic`/`shop` are `String`, not that they are authenticated.

### Impact Explanation
An attacker who has obtained just one validly-signed webhook body from Shopify (trivially available by installing the target app on their own free development shop) can cause the app to execute the handler for *any topic it has registered*, and can make that handler believe the event originated from *any shop* the attacker chooses — including a victim merchant's shop. This is a cross-tenant confusion / forged-webhook-accepted-as-authentic vulnerability: the app's own signature check (the only authentication mechanism for webhooks) passes for a payload/topic/shop combination Shopify never actually produced or signed together. If the app's handlers key any privileged action (data deletion, uninstall cleanup, order processing, GDPR redaction, session/token invalidation) off `topic` and `shop` from `WebhookMetadata`, the attacker can trigger those actions against a shop they do not control, using their own single genuine webhook as the "signature donor." This is repeatable indefinitely and against arbitrary victim shop domains, matching the Critical - authentication bypass category (a forged/mismatched request accepted as authentic).

### Likelihood Explanation
Preconditions are minimal and fully within the unprivileged attacker's reach: create a free development shop, install the target app, let at least one webhook be delivered (any topic the app subscribes to). No `api_secret_key` or other credential is ever needed — the attacker never computes an HMAC themselves, they only replay one that Shopify already computed for their own account, while altering unauthenticated headers. Attacker cost is a single HTTP request; feasibility is high since it requires no timing tricks, no dependency on TLS interception, and no special app configuration beyond having handlers registered for more than one topic (the default state of any real app).

### Recommendation
Include `topic`, `shop-domain`, and ideally `webhook_id`/API version in the material that is cryptographically bound to the request before it can be trusted, or independently re-derive/verify these values out of band:
- Change `Request#to_signable_string` (or add a parallel verification step) so the HMAC check is bound to the exact `(shop, topic, body)` tuple actually used for dispatch — since Shopify's HMAC is computed only over the raw body, the app-side fix must instead enforce that `topic` and `shop` are cross-checked against trusted app state (e.g. only dispatch to handlers for shops known to have an active, valid session/install, and reject if the shop is not an installed shop) rather than trusting the headers unconditionally.
- Apply `Utils::ShopValidator.sanitize!` (or equivalent) to `request.shop` and cross-reference it against the app's known installed shops before invoking any handler.
- In `Registry.process`, keep excluding `MANDATORY_TOPICS` from ad-hoc dispatch (or otherwise ensure mandatory/compliance topics get extra scrutiny), consistent with how `register` treats them.

### Proof of Concept
minitest + WebMock/Mocha plan under `test/webhooks/registry_test.rb`:
1. Register two `FakeWebhookHandler`s under two different topics, e.g. `"topic/a"` with handler A (records shop+topic it was invoked with) and `"topic/b"` with handler B.
2. Compute a single valid HMAC for body `"{}"` using `ShopifyAPI::Context.api_secret_key` (as in the existing `setup` in `registry_test.rb`).
3. Build a `Webhooks::Request` with headers `x-shopify-topic: "topic/a"`, `x-shopify-shop-domain: "attacker-shop.myshopify.com"`, that valid hmac, and body `"{}"`; call `Registry.process` and assert handler A is invoked with `shop == "attacker-shop.myshopify.com"`.
4. Build a second `Webhooks::Request` with the **same** body and **same** hmac, but headers changed to `x-shopify-topic: "topic/b"`, `x-shopify-shop-domain: "victim-shop.myshopify.com"`. Call `Registry.process`.
5. Assert (to demonstrate the vulnerability) that `Utils::HmacValidator.validate` still returns `true` for this second request, and that handler B is invoked with `shop == "victim-shop.myshopify.com"` — proving dispatch followed the unsigned headers rather than anything bound by the signature, i.e. the same signed artifact was accepted for two different topic/shop combinations Shopify never issued together. [4](#0-3) [5](#0-4) [6](#0-5)

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L10-38)
```ruby
      sig { override.returns(String) }
      def hmac
        Digest.hexencode(Base64.decode64(T.cast(shopify_header("hmac-sha256"), String)))
      end

      sig { returns(String) }
      def topic
        T.cast(shopify_header("topic"), String)
      end

      sig { returns(String) }
      def shop
        T.cast(shopify_header("shop-domain"), String)
      end

      sig { returns(String) }
      def api_version
        T.cast(shopify_header("api-version"), String)
      end

      sig { returns(String) }
      def webhook_id
        T.cast(shopify_header("webhook-id"), String)
      end

      sig { override.returns(String) }
      def to_signable_string
        @raw_body
      end
```

**File:** lib/shopify_api/utils/hmac_validator.rb (L12-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery).returns(T::Boolean) }
        def validate(verifiable_query)
          return false unless verifiable_query.hmac

          result = validate_signature(verifiable_query, Context.api_secret_key)
          if result || Context.old_api_secret_key.nil? || T.must(Context.old_api_secret_key).empty?
            result
          else
            validate_signature(verifiable_query, T.must(Context.old_api_secret_key))
          end
        end

        private

        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
```

**File:** lib/shopify_api/webhooks/registry.rb (L188-200)
```ruby
        sig { params(request: Request).void }
        def process(request)
          raise Errors::InvalidWebhookError, "Invalid webhook HMAC." unless Utils::HmacValidator.validate(request)

          handler = @registry[request.topic]&.handler

          unless handler
            raise Errors::NoWebhookHandler, "No webhook handler found for topic: #{request.topic}."
          end

          handler.handle(data: WebhookMetadata.new(topic: request.topic, shop: request.shop,
            body: request.parsed_body, api_version: request.api_version, webhook_id: request.webhook_id))
        end
```
