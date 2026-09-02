### Title
Webhook `shop-domain` (and `topic`/`webhook-id`) headers are not covered by the HMAC signature, allowing cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` implements `Utils::VerifiableQuery` but signs only the raw HTTP body, not the `shopify-shop-domain`, `shopify-topic`, or `shopify-webhook-id` headers. `Registry.process` validates the HMAC and then unconditionally trusts these unauthenticated headers to build the `WebhookMetadata` that is handed to the app's handler. This breaks the identity binding `HMAC-signed bytes == data acted upon`, exactly the bug class described in the analog report (a field acted on but not covered by the HMAC).

### Finding Description
`Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

Meanwhile `shop`, `topic`, `webhook_id`, and `api_version` are all read directly from attacker-controllable HTTP headers, independent of the signed payload: [2](#0-1) 

`Utils::HmacValidator.validate` recomputes the HMAC over `to_signable_string` (i.e. the body only) and compares it to the `hmac-sha256` header: [3](#0-2) 

`Registry.process` calls this validator, and once it passes, builds `WebhookMetadata` directly from the *unauthenticated* `request.shop`, `request.topic`, and `request.webhook_id` fields: [4](#0-3) 

Because Shopify signs webhooks with the app's single `client_secret` (shared across every shop that installs the app), a merchant who has the app installed on their own shop legitimately receives webhooks with a valid HMAC over some raw body. That same merchant can resend that exact `(raw_body, hmac-sha256)` pair to the app's webhook endpoint while forging the `shopify-shop-domain` header to name a *different* shop (or forging `shopify-topic`/`shopify-webhook-id`). `HmacValidator.validate` still returns `true` because it only checks the body bytes, and `Registry.process` forwards the attacker-chosen `shop` value straight to the host application's handler as if it were authentic. The binding that should hold — `hmac_verified_bytes == (body, shop, topic)` — is broken to `hmac_verified_bytes == body only`, while `shop`/`topic` are parsed independently and passed on as trusted.

This is the webhook-processing analog of the `safeTransferFrom`-style report: an operation trusts an unverified/uncovered piece of data (there, an implicit approval; here, the shop/topic identity) as if it had been checked, letting an unprivileged actor manufacture events attributed to another tenant.

### Impact Explanation
Any app built on this gem that uses `request.shop` from `WebhookMetadata` to select which merchant/session/access-token context to act on (the pattern the library's own docs recommend, see `docs/usage/webhooks.md`) is exposed to cross-tenant webhook injection: an attacker who runs the app on their own store can forge events (order created, app uninstalled, GDPR requests, etc.) that appear to originate from a victim shop, without ever possessing the victim's credentials. This falls under the "cross-tenant access" Critical impact category, since it lets one authenticated-but-unprivileged tenant inject data/state associated with another tenant purely through this gem's verification gap.

### Likelihood Explanation
Likelihood is meaningfully high: obtaining a body/HMAC pair is trivial (install the app on any store and capture one real webhook), and only the `shop-domain` (or `topic`/`webhook-id`) header of the replayed request needs to be altered — no secrets, tokens, or privileged access are required. The vulnerable code path (`Request#to_signable_string`, `HmacValidator.validate`, `Registry.process`) is exercised on every webhook the host app processes via this gem's documented integration.

### Recommendation
Include the identity-critical headers (`shop-domain`, `topic`, and ideally `webhook-id`) in the signed/verified material, or otherwise cryptographically bind them to the HMAC check — e.g. verify the HMAC as Shopify intends (body-only) but require the host app to compare `shop` against the shop for which it expects webhooks in that context rather than trusting the header unconditionally, and document this loudly. At minimum, `Request#to_signable_string` should not be the sole gate that callers rely on for authenticating `shop`; `Registry.process`/`WebhookMetadata` should not present `shop`/`topic` as verified when only the body was verified.

### Proof of Concept
1. Install the app on `attacker-shop.myshopify.com`; capture one real webhook delivery, e.g. `orders/create`, noting `raw_body`, `shopify-hmac-sha256`, and that `HmacValidator.validate` succeeds.
2. POST the identical `raw_body` and `shopify-hmac-sha256` to the app's webhook endpoint, but replace the header `shopify-shop-domain: attacker-shop.myshopify.com` with `shopify-shop-domain: victim-shop.myshopify.com`.
3. `ShopifyAPI::Webhooks::Request.new` accepts the forged header, `Utils::HmacValidator.validate(request)` returns `true` (it only checked `raw_body`), and `Registry.process` invokes the handler with `WebhookMetadata#shop == "victim-shop.myshopify.com"`, even though the payload actually came from, and was signed for, `attacker-shop.myshopify.com`.

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
