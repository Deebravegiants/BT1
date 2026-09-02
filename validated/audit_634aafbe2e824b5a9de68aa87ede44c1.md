### Title
Webhook shop/topic identity is trusted from unauthenticated headers while the HMAC only signs the raw body — (`lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` signs and verifies only the raw HTTP body, but the tenant-identifying fields (`shop-domain`, `topic`, `webhook-id`, `api-version`) that `Registry.process` hands to the app's handler are read straight from HTTP headers that are never covered by the HMAC. This breaks the intended binding `hmac_verified(bytes) == identity_of(shop, topic)`.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

The `shop`, `topic`, `webhook_id`, and `api_version` accessors are parsed directly from headers with no cryptographic binding to the signed body: [2](#0-1) 

`Registry.process` validates the HMAC over that same unbound `raw_body`, and — once validation passes — unconditionally trusts `request.shop`, `request.topic`, and `request.webhook_id` (all header-derived, unsigned) to construct the `WebhookMetadata` dispatched to the app's handler: [3](#0-2) 

`HmacValidator.validate` only proves that the *bytes* of `to_signable_string` (the body) were signed with the app's secret; it proves nothing about which shop or topic those bytes are being associated with: [4](#0-3) 

This is exactly the analog class called out in the rules: *"bytes verified versus bytes parsed"* / *"a shop authenticated versus the shop... acted on but not covered by the HMAC"*. The equality that should hold — `shop_bound_by_signature == shop_used_for_dispatch` — does not hold, because the signature never covers `shop`.

### Impact Explanation
Any unprivileged internet user who can create their own Shopify dev store and install the target app (a normal, unprivileged action) receives one legitimate webhook delivery: a `(raw_body, hmac)` pair that is valid under the app's `api_secret_key`, addressed to their own shop. Because the header fields are outside the signature, that attacker can resend the identical `raw_body`/`x-shopify-hmac-sha256` pair directly to the app's public webhook endpoint while substituting `x-shopify-shop-domain` (and `x-shopify-topic`) for a victim shop. `HmacValidator.validate` still succeeds (it only checks the body bytes), and `Registry.process` dispatches a `WebhookMetadata` claiming the event came from the victim shop. If the host application uses `data.shop` to key privileged, per-tenant side effects (data writes, deletions, or the mandatory `shop/redact` / `customers/redact` / `customers/data_request` compliance topics that this gem specifically special-cases), the attacker achieves cross-tenant data corruption or triggers destructive privacy-workflow actions against a shop they do not control.

### Likelihood Explanation
Obtaining a genuine `(body, hmac)` pair requires only installing the app on a free dev store — no secret, no token, and no privileged account are needed, satisfying the "unprivileged internet user" constraint. Replaying it against the app's publicly documented webhook path with a modified `shop-domain` header is a straightforward HTTP-level forgery once the pair is captured.

### Recommendation
Bind the tenant/topic identity into the signed payload verification path: reject requests where `hmac` was not computed jointly over the body and the asserted `shop`/`topic` (as Shopify's outbound signing already does per-delivery), or require the caller to separately confirm that the `shop` header corresponds to a session/registration the app already trusts before dispatching `WebhookMetadata`, rather than trusting the header value implicitly once body-only HMAC validation succeeds.

### Proof of Concept
1. Attacker creates a free dev store `attacker.myshopify.com` and installs the target app; Shopify delivers a real webhook (e.g. `orders/create`) to the app's endpoint with a valid `x-shopify-hmac-sha256` over the JSON body and header `x-shopify-shop-domain: attacker.myshopify.com`.
2. Attacker captures the exact raw body bytes and the `x-shopify-hmac-sha256` value from that delivery.
3. Attacker crafts a new POST to the same webhook endpoint with the identical body and `x-shopify-hmac-sha256`, but sets `x-shopify-shop-domain: victim.myshopify.com` (and, if desired, `x-shopify-topic: shop/redact`).
4. `ShopifyAPI::Utils::HmacValidator.validate` in `Registry.process` (`lib/shopify_api/webhooks/registry.rb:188-190`) verifies successfully because it only checks `raw_body` against the secret.
5. The handler receives `WebhookMetadata.new(shop: "victim.myshopify.com", topic: "shop/redact", ...)` and the host app performs its shop-scoped side effect against `victim.myshopify.com`, despite the request never having been authenticated as originating from that shop.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L15-33)
```ruby
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
```

**File:** lib/shopify_api/webhooks/request.rb (L35-38)
```ruby
      sig { override.returns(String) }
      def to_signable_string
        @raw_body
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
