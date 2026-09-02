### Title
Webhook HMAC only signs the request body, not the `shop-domain` header, enabling cross-tenant webhook spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw request body, while `ShopifyAPI::Webhooks::Registry.process` trusts the `shop`, `topic`, `webhook_id`, and `api_version` values taken from unauthenticated HTTP headers and hands them to the app's handler as the tenant identity for the event. Because the app's `api_secret_key` is shared across every shop that installs the app, any merchant (an unprivileged internet user who can freely install the public app on their own store) can capture one of their own legitimately-signed webhook deliveries and replay the same body/HMAC pair with a forged `x-shopify-shop-domain` header pointing at a victim shop. The HMAC check still passes because it never covers the shop header, so the handler executes believing the event originated from the victim tenant.

### Finding Description
`HmacValidator.validate` verifies `verifiable_query.to_signable_string` against the computed HMAC: [1](#0-0) 

For webhooks, `to_signable_string` is defined to be exactly the raw body — none of the Shopify-supplied headers participate in the signature: [2](#0-1) 

Yet the `shop`, `topic`, `webhook_id`, and `api_version` accessors — all read straight from headers with zero cryptographic binding — are exactly the fields `Registry.process` forwards to the app's business logic as trusted identity/context after the HMAC check succeeds: [3](#0-2) [4](#0-3) 

Because `Context.api_secret_key` is a single shared secret used for every installation of the app, not a per-shop secret, an unprivileged user who has installed the app on their own shop can obtain a genuinely valid `(body, hmac)` pair, then replay that pair with the `x-shopify-shop-domain` header rewritten to any other shop domain. The identity binding that should hold — `hmac-verified sender == shop attributed to the event` — is broken: the HMAC only proves "some body byte sequence was produced with the shared secret", not "this specific shop sent this specific event."

### Impact Explanation
This is a cross-tenant access vulnerability (Critical): any app that uses `shop` from `WebhookMetadata` to select per-tenant state (session lookup, data deletion on `app/uninstalled`, order/customer processing, billing changes, etc.) can be made to apply attacker-chosen webhook content to a victim shop's tenant context, without the attacker ever needing credentials for the victim shop.

### Likelihood Explanation
Likelihood is high for any app author following the documented pattern (`Registry.process`/`WebhookMetadata`) exactly as designed, since nothing in the gem's public API signals that the `shop` field is unauthenticated. The only prerequisite for an attacker is the ability to install the public app on a shop they control — a normal, unprivileged action for any Shopify merchant/developer — plus the ability to send an HTTP POST to the app's public webhook endpoint with modified headers, which requires no special access.

### Recommendation
Include the identity-carrying headers (`shop`, `topic`, `webhook_id`, `api_version`) in the HMAC-signed content, or otherwise cryptographically bind them (e.g., re-derive/verify shop identity through a side channel such as a stored per-shop token) before trusting `request.shop` in `Registry.process`. Short term, document loudly that `request.shop`/`data.shop` is unauthenticated and must be cross-checked against a known/installed shop list before being used for tenant-scoped actions.

### Proof of Concept
1. Attacker installs the target app on their own store `attacker.myshopify.com`.
2. Shopify sends a legitimate webhook to the app's endpoint:
   ```
   x-shopify-topic: orders/create
   x-shopify-hmac-sha256: <valid HMAC of BODY>
   x-shopify-shop-domain: attacker.myshopify.com
   ```
3. Attacker records `BODY` and the accompanying `x-shopify-hmac-sha256` value (fully visible to them as the receiving webhook owner, or reproducible since they control the content that generated it).
4. Attacker re-POSTs the exact same `BODY` and `x-shopify-hmac-sha256` to the app's webhook endpoint but sets:
   ```
   x-shopify-shop-domain: victim-shop.myshopify.com
   ```
5. `HmacValidator.validate` recomputes the HMAC over `BODY` only (per `Request#to_signable_string`) using the app's shared `api_secret_key`, which matches — validation succeeds.
6. `Registry.process` invokes the app's handler with `WebhookMetadata.new(shop: "victim-shop.myshopify.com", topic: "orders/create", body: <attacker-controlled>, ...)`, causing the app to process attacker-controlled data attributed to the victim tenant.

### Citations

**File:** lib/shopify_api/utils/hmac_validator.rb (L12-22)
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
```

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
