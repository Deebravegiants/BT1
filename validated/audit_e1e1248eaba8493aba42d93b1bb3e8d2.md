### Title
Webhook HMAC does not bind the `shop-domain` / `topic` headers, enabling cross-tenant webhook forgery - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC-signable content from the raw body only, while `shop`, `topic`, `webhook_id`, and `api_version` are read straight from HTTP headers that are never included in the signature. `Registry.process` trusts these header-derived values once the body's HMAC checks out, so an attacker who possesses any single valid `(raw_body, hmac)` pair for the app's `api_secret_key` can replay it with a forged `shop-domain`/`topic` header and have it accepted as an authentic webhook for a different shop/topic.

### Finding Description
`Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

Meanwhile `shop`, `topic`, `webhook_id`, and `api_version` are parsed directly from headers, independent of the HMAC: [2](#0-1) 

`HmacValidator.validate` only verifies that `hmac` matches `to_signable_string` (i.e., the body) against the shared `api_secret_key`: [3](#0-2) 

`Registry.process` performs exactly that body-only check, then dispatches the handler using the *unverified* `request.topic` and `request.shop`: [4](#0-3) 

The equality that should hold is: `shop_bound_by_hmac == shop_used_for_tenant_routing`. Here, the HMAC only binds `raw_body`, so `shop_bound_by_hmac` is undefined/empty, while `shop_used_for_tenant_routing = request.shop` (an unauthenticated header value). Any actor capable of obtaining one legitimately-signed webhook body (e.g., a low-privilege shop that installed the app receives real webhooks signed with the shared `api_secret_key`) can resend that exact body with a spoofed `shopify-shop-domain` (or `x-shopify-shop-domain`) header — and, separately, a spoofed `shopify-topic` header — pointing at a different tenant or a more sensitive topic, and the request still passes `HmacValidator.validate` because the header content was never part of the signed bytes.

### Impact Explanation
This breaks the tenant/topic identity binding for webhook processing: an unprivileged actor (any shop that has installed the app, or anyone who captures one delivered webhook) can make the app process attacker-chosen `shop`/`topic` values against a validly-signed body, causing the host app's webhook handler to run business logic attributed to a shop it does not control. Since Shopify apps typically use `shop` to select per-tenant storage/session context in the handler (`WebhookMetadata#shop`), this is a cross-tenant data integrity/access issue — the impact category explicitly listed as Critical in scope ("cross-tenant access").

### Likelihood Explanation
Reaching this requires only the ability to submit an HTTP POST to the app's webhook endpoint with attacker-controlled headers and a previously-observed valid `(raw_body, hmac)` pair — no access token, `client_secret`, or privileged account is needed. Any shop that installs the app receives such valid pairs as part of normal Shopify webhook delivery, making exploitation straightforward for any unprivileged tenant of a multi-tenant app built on this gem.

### Recommendation
Include the identifying headers (`shop-domain`, `topic`, and ideally `api-version`/`webhook-id`) in the HMAC-signed content, or otherwise cryptographically bind them to the signature (e.g., derive the signable string from a canonical concatenation of headers + body) so that `HmacValidator.validate` fails whenever any of these header values are altered relative to what Shopify actually signed.

### Proof of Concept
1. App receives a legitimate Shopify webhook for `shop-a.myshopify.com`, topic `carts/update`, with raw body `{}` and header `x-shopify-hmac-sha256: <valid-hmac-of-{}>`.
2. Attacker (who owns `shop-a` or intercepted the delivery) resends the exact same body and HMAC header to the app's webhook endpoint, but sets `x-shopify-shop-domain: victim-shop.myshopify.com` and `x-shopify-topic: orders/paid`.
3. `ShopifyAPI::Webhooks::Request.new` parses the forged headers normally, and `HmacValidator.validate` in `Registry.process` returns `true` because it only checks `raw_body` against the HMAC — the forged `shop`/`topic` are never validated. [5](#0-4) 
4. The registered `orders/paid` handler runs with `WebhookMetadata(shop: "victim-shop.myshopify.com", body: {})`, i.e., the app processes a forged event under another tenant's identity.

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

**File:** lib/shopify_api/webhooks/registry.rb (L188-199)
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
```
