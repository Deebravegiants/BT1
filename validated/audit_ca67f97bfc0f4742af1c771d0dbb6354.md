### Title
Webhook `shop-domain` (and `topic`/`api-version`/`webhook-id`) header is not covered by the HMAC signature, enabling cross-tenant shop spoofing on replayed webhooks - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw HTTP body, while `shop`, `topic`, `api_version`, and `webhook_id` are read directly from unauthenticated HTTP headers. `Utils::HmacValidator.validate` (used by `Registry.process`) only checks that the raw body matches the HMAC — it never binds the `shop-domain` header to the signature. This breaks the identity binding: `shop_authenticated == shop_used_by_handler` does not hold, because only the body is authenticated while the shop that the handler acts on is taken from an unauthenticated header.

### Finding Description
`ShopifyAPI::Webhooks::Request` implements `Utils::VerifiableQuery`: [1](#0-0) 

Note that `hmac` decodes the `x-shopify-hmac-sha256`/`shopify-hmac-sha256` header, and `to_signable_string` returns `@raw_body` — nothing else. `shop`, `topic`, `api_version`, and `webhook_id` are all pulled straight from headers with no cryptographic binding to the signature: [2](#0-1) 

`HmacValidator.validate` computes the signature only over `to_signable_string` (i.e., the raw body) and compares it to the received HMAC: [3](#0-2) 

`Registry.process` validates the HMAC and then dispatches directly using the untrusted `request.shop`, `request.topic`, `request.api_version`, and `request.webhook_id` to build the `WebhookMetadata` handed to the app's handler: [4](#0-3) 

Since the app's webhook endpoint is a plain public HTTP endpoint (any unprivileged internet user can POST to it directly, bypassing Shopify's delivery infrastructure entirely), an attacker who is able to obtain any one valid `(raw_body, hmac)` pair — for example by installing/operating their own trial Shopify store and capturing the exact webhook payload and its valid `x-shopify-hmac-sha256` value that Shopify sent them — can replay that identical body+HMAC to the victim app's webhook endpoint while substituting an arbitrary `x-shopify-shop-domain` header (and/or `x-shopify-topic`/`x-shopify-webhook-id`/`x-shopify-api-version`). `HmacValidator.validate` still passes because it only checks the body content against the secret, and `Registry.process` will happily dispatch the (attacker's own, legitimately-signed) body to the handler tagged with a forged, arbitrary victim `shop` value.

This is precisely the "field acted on but not covered by the HMAC" identity-binding failure class: the equality that should hold is `hmac_signed_shop == handler_dispatch_shop`, but in this code the HMAC signs only the body, so `handler_dispatch_shop` is fully attacker-controlled while `hmac_signed_shop` doesn't exist at all.

### Impact Explanation
Any application built on this gem that relies on `WebhookMetadata#shop` (or `#topic`/`#webhook_id`) inside its webhook handler to key merchant records, trigger per-tenant side effects (e.g., "delete this shop's data", "mark this shop uninstalled", "update this shop's order/inventory record") is exposed to cross-tenant data corruption/access: an attacker can cause the handler logic to execute against an arbitrary victim shop identifier while supplying attacker-controlled (but legitimately-HMAC-signed for their own data) body content. This matches the Critical "cross-tenant access" impact bucket, since a request from one tenant (or an unprivileged attacker with any trial account) can be attributed to and acted on behalf of a different tenant.

### Likelihood Explanation
Requires no possession of `api_secret_key`, access tokens, or the app's `client_secret`. The only prerequisite is the attacker's ability to obtain one legitimately-signed webhook body+HMAC pair (trivially available to any developer with a free/trial Shopify store that installs the app or triggers any webhook topic) and the ability to POST directly to the target app's public webhook endpoint with custom headers — both of which are available to an unprivileged internet user. The actual severity is bounded by how much the consuming application trusts `WebhookMetadata#shop`/`#topic` for tenant-scoped side effects, but the gem itself provides no protection and documents/exposes `shop` as if it were verified.

### Recommendation
Do not treat `shop`, `topic`, `api_version`, or `webhook_id` headers as trusted merely because `HmacValidator.validate` passed. Either:
1. Include the relevant identity headers (`shop-domain`, `topic`, `webhook-id`) in the signable content used for HMAC verification (this would require aligning with Shopify's actual webhook signing scheme, which currently only signs the body — so this may require an out-of-band verification step), or
2. Require the consuming application to cross-check `request.shop` against a known/registered shop for the webhook subscription (e.g., validated via `get_webhook_id`/registry lookup) before trusting it for tenant-scoped side effects, and clearly document that `Request#shop`/`#topic`/`#webhook_id` are **not** cryptographically authenticated by `HmacValidator.validate` — only the raw body is.

### Proof of Concept
1. Attacker creates/uses any Shopify development/trial store and installs a webhook subscription (or captures any webhook delivery) to observe one legitimate `(raw_body, x-shopify-hmac-sha256)` pair generated by Shopify for their own shop.
2. Attacker sends a raw HTTP POST directly to the victim app's public webhook endpoint (bypassing Shopify) with:
   - Body: the exact captured `raw_body`
   - Header `x-shopify-hmac-sha256`: the exact captured HMAC value
   - Header `x-shopify-shop-domain`: `victim-shop.myshopify.com` (arbitrary, attacker-chosen)
   - Header `x-shopify-topic`: any registered topic
3. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which succeeds because it only recomputes the HMAC over `raw_body`, matching the captured (legitimate) signature — see: [5](#0-4) 
4. The app's handler is invoked with `WebhookMetadata.shop == "victim-shop.myshopify.com"`, even though that value was never authenticated, causing any tenant-scoped logic in the handler to run against the wrong (or attacker-chosen arbitrary) shop identity.

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
