### Title
Webhook tenant identity (`shop`) is not bound by the HMAC signature - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC-signable content from the raw request body only, while the `shop` (and `topic`/`webhook_id`) values used to dispatch the webhook to a merchant-specific handler are read directly from unauthenticated HTTP headers. This breaks the binding `shop_authenticated == shop_acted_on`, allowing a party who possesses one valid `(body, hmac)` pair to relabel it as belonging to a different, victim shop.

### Finding Description
`Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`Request#shop`, `#topic`, and `#webhook_id` are parsed straight from headers and are never part of the signed material: [2](#0-1) 

`Registry.process` validates only the HMAC of the body, then forwards `request.shop` (an unverified value) as the tenant identifier to the app's handler: [3](#0-2) 

`HmacValidator.validate` in turn calls `verifiable_query.to_signable_string`, i.e. it validates the bytes of the body, not the bytes that carry the shop identity used downstream: [4](#0-3) 

Equality that should hold but does not:
`shop_verified_by_hmac == shop_delivered_to_handler`

Before the request: Shopify computes `hmac = HMAC(api_secret_key, body)` and separately sets the `X-Shopify-Shop-Domain` header to the real shop for the webhook's origin store.
After an attacker's request: the attacker resends the exact same `body`/`hmac` pair but substitutes an arbitrary value in the `shop-domain` header. `HmacValidator.validate` still succeeds (it only checks the body), and `Registry.process` calls the handler with `WebhookMetadata.new(... shop: request.shop ...)` using the attacker-supplied shop value, not the shop that actually produced the signed payload.

### Impact Explanation
This is a cross-tenant identity confusion: the gem hands the app's business logic a `shop` value that was never bound by the cryptographic check the app relies on for authenticity. Any app that uses `WebhookMetadata#shop` to select which merchant's session/access token/data to update (a very common pattern, e.g. reacting to `app/uninstalled`, `shop/update`, or data-sync webhooks) can be made to act on shop B's behalf while consuming a payload legitimately signed for shop A. Because a genuine `(body, hmac)` pair can be obtained by anyone who runs the app on their own store (a normal, unprivileged action for public apps) and Shopify will deliver such payloads with a valid HMAC computed from the app's own secret, this crosses a tenant boundary without requiring the app's `api_secret_key`, an access token, or any privileged account — satisfying the Critical "cross-tenant access" bar.

### Likelihood Explanation
Any user who can install the target app on a shop they control receives genuine webhook deliveries with valid `(body, hmac)` pairs signed by Shopify using the app's secret. Replaying that request to the app's webhook endpoint with only the `shop-domain` (and optionally `topic`/`webhook-id`) header changed requires no cryptographic material beyond what was already delivered to the attacker, and the gem performs no comparison between the header-derived shop and any value bound into the signed body.

### Recommendation
Include the identity fields that are acted upon — at minimum `shop`, and ideally `topic`/`webhook_id` — in the HMAC-covered signable content (or otherwise cryptographically bind them, e.g. via a per-shop secret or a MAC over `header||body`), so that `Registry.process` cannot dispatch a validated-body request under a `shop` value that was not part of the same signed message.

### Proof of Concept
1. Attacker installs the target Shopify app on their own store `attacker-shop.myshopify.com` and triggers a webhook topic the app also uses to react to sensitive changes (e.g. `app/uninstalled`).
2. Shopify delivers the webhook with a body `B` and header `X-Shopify-Hmac-Sha256: HMAC(api_secret_key, B)`; the attacker captures this full request.
3. Attacker resends the identical body `B` and identical `hmac` header to the app's webhook endpoint, but changes `X-Shopify-Shop-Domain` to `victim-shop.myshopify.com`.
4. `HmacValidator.validate` succeeds because `to_signable_string` only checks `B`, per [1](#0-0) .
5. `Registry.process` invokes the registered handler with `shop: "victim-shop.myshopify.com"`, per [5](#0-4) , causing the app to act on the victim shop's tenant context using attacker-controlled/attacker-shop-derived payload data.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L15-23)
```ruby
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
