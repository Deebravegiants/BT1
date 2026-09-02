## Analog Found: Webhook shop identity not bound to the HMAC signature — cross‑tenant webhook spoofing

### Title
Webhook Shop Identity Not Covered by HMAC, Enabling Cross-Tenant Webhook Spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
The reported bug class is "a field is acted upon but not actually covered by the code that is supposed to authenticate it." In `ShopifyAPI::Webhooks::Request`, the HMAC signature is computed only over the raw request body, while the `shop` (merchant identity) is taken from an unauthenticated HTTP header. `ShopifyAPI::Webhooks::Registry.process` then hands this unverified `shop` value straight to the app's webhook handler, breaking the equality `shop_verified_by_hmac == shop_used_by_handler`.

### Finding Description
`Request#to_signable_string` returns only the raw body, and `Request#hmac` is read from the `hmac-sha256` header: [1](#0-0) [2](#0-1) 

`Utils::HmacValidator.validate` verifies `computed_signature == received_signature` where `computed_signature` is `HMAC(api_secret_key, verifiable_query.to_signable_string)`, i.e. `HMAC(api_secret_key, raw_body)` only: [3](#0-2) 

`Registry.process` validates this body-only HMAC, then forwards `request.shop` (from the `x-shopify-shop-domain` / `shopify-shop-domain` header, which is not part of the signed payload) directly into `WebhookMetadata` passed to the app's handler: [4](#0-3) [5](#0-4) 

Because the `api_secret_key` (client secret) is shared across **all** merchants who install a given app, any unprivileged internet user who can obtain one legitimately-signed webhook payload (e.g., by installing the app on their own shop and triggering a webhook event on their own data — a routine, credential-free action) possesses a valid `(raw_body, hmac)` pair. Since `shop` is not part of the signed material, that same `(raw_body, hmac)` pair can be replayed with the `shop` header changed to any victim `myshopify.com` domain, and `HmacValidator.validate` will still accept it because it never inspects `shop` at all — it only recomputes the HMAC over the body.

This is the direct identity-binding break described in the class of bug: `shop authenticated ≠ shop used by handler`. Downstream, `WebhookMetadata.new(... shop: request.shop ...)` is passed to whatever handler the app registered, and the host app is expected to trust `data.shop` as the tenant the payload belongs to — exactly per this gem's own documented contract.

### Impact Explanation
This crosses the tenant boundary this gem is responsible for maintaining: an attacker with a normal, unprivileged Shopify store (no special access, no leaked secrets) can cause a merchant app to process attacker-controlled webhook content while attributing it to an arbitrary victim shop domain. Depending on the app's webhook handler (e.g., orders/create, customers/update, app/uninstalled), this can lead to cross-tenant data corruption or to the attacker forcing state changes (e.g. faking an `app/uninstalled` event for a victim shop, or injecting fabricated order/customer data attributed to the victim) — a cross-tenant access impact.

### Likelihood Explanation
High feasibility: the only prerequisite is a free, ordinary Shopify development/trial store where the attacker can install the target app and legitimately receive at least one properly signed webhook (any topic the app subscribes to). No access token, no `api_secret_key`, and no privileged account are required — this satisfies the "unprivileged internet user" constraint. The replay itself is a single crafted HTTP POST with a substituted `shop` header, reusing the untouched, still-valid `hmac-sha256`/body pair.

### Recommendation
Bind the `shop` (and ideally `topic`/`webhook-id`) into the HMAC-verified payload, or otherwise independently verify that the `shop` header value corresponds to a shop the app is actually installed on/has an active session for, before dispatching to handlers. At minimum, `Request#to_signable_string` (or the validator) should authenticate the shop-domain header as part of the accepted signature material rather than trusting it verbatim from `Registry.process`.

### Proof of Concept
1. Attacker creates a normal Shopify dev/trial store `attacker-shop.myshopify.com` and installs the target app (no special privilege needed).
2. Attacker triggers a webhook event (e.g. updates an order) on their own store; the app's endpoint receives a legitimately signed webhook: body `B`, header `x-shopify-hmac-sha256: H`, header `x-shopify-shop-domain: attacker-shop.myshopify.com`.
3. Attacker replays the exact same request to the app's public webhook endpoint but changes only `x-shopify-shop-domain` to `victim-shop.myshopify.com`. `H` and `B` are unchanged.
4. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes `HMAC(api_secret_key, B)` and compares to `H` — this matches because `B` and `H` are untouched (see `lib/shopify_api/webhooks/request.rb:35-38` and `lib/shopify_api/utils/hmac_validator.rb:26-31`).
5. Validation passes; `Registry.process` invokes the app's handler with `WebhookMetadata(shop: "victim-shop.myshopify.com", body: <attacker's data>, ...)` (`lib/shopify_api/webhooks/registry.rb:198-199`), causing the app to act on attacker data as though it belongs to the victim shop.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L10-23)
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
```

**File:** lib/shopify_api/webhooks/request.rb (L35-38)
```ruby
      sig { override.returns(String) }
      def to_signable_string
        @raw_body
      end
```

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
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
