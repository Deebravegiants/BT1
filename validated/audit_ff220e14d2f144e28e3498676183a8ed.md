This confirms the vulnerability: `ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`, while `shop`, `topic`, `webhook_id`, and `api_version` are read directly from unauthenticated HTTP headers and are never part of the HMAC-signed content. `Registry.process` validates the HMAC solely against the body and then trusts `request.shop`/`request.topic` to build `WebhookMetadata`, which is the app-facing tenant identity used to route/attribute webhook data. [1](#0-0) [2](#0-1) 

### Title
Webhook shop/topic identity not bound to HMAC, enabling cross-tenant webhook forgery via replay - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request` computes the verifiable signable string from the raw body only, while the `shop`, `topic`, `webhook_id`, and `api_version` values used by `ShopifyAPI::Webhooks::Registry.process` (and passed to the app's handler as trusted `WebhookMetadata`) come from HTTP headers that are not covered by the HMAC. This breaks the intended binding `HMAC valid ⇒ shop/topic authentic`, allowing a party who possesses one validly-signed webhook body (e.g. genuine webhook traffic Shopify sends them for their own installed shop) to replay that exact body+HMAC to the app's public webhook endpoint while forging the `shopify-shop-domain`/`shopify-topic` headers to any value, causing the app to process attacker-supplied data as if it originated from a different tenant/topic.

### Finding Description
`Request#to_signable_string` is defined as:
```ruby
def to_signable_string
  @raw_body
end
``` [3](#0-2) 

`Utils::HmacValidator.validate` computes `OpenSSL::HMAC.hexdigest` over exactly this signable string using `Context.api_secret_key` and compares it to the `hmac` value read from the header, then returns true/false; it never inspects `shop`, `topic`, or other headers. [4](#0-3) 

Meanwhile `shop`, `topic`, `webhook_id`, and `api_version` are all pulled straight from attacker-controllable HTTP headers with no cryptographic tie to the HMAC:
```ruby
def shop
  T.cast(shopify_header("shop-domain"), String)
end
``` [5](#0-4) 

`Registry.process` validates the HMAC and then immediately trusts these header-derived values to build the `WebhookMetadata` struct handed to the app's webhook handler, which the gem's own documentation says represents "the shop domain of the webhook":
```ruby
raise Errors::InvalidWebhookError, "Invalid webhook HMAC." unless Utils::HmacValidator.validate(request)
handler = @registry[request.topic]&.handler
...
handler.handle(data: WebhookMetadata.new(topic: request.topic, shop: request.shop,
  body: request.parsed_body, api_version: request.api_version, webhook_id: request.webhook_id))
``` [2](#0-1) [6](#0-5) 

This is precisely the identity-binding class described in the report: a field that is *acted on* (`shop`, used by the app to attribute/route data to a tenant) is not covered by the HMAC that is supposed to authenticate the whole message. The equality the gem implicitly claims to hold is:
`HMAC_valid(request) ⇒ request.shop == the shop that actually produced request.parsed_body`

But because `to_signable_string` only commits to `@raw_body`, this equality does not hold: `HMAC_valid` only proves "this body was signed by our api_secret_key at some point for some shop," not "this body+shop pairing is authentic." Any party that has ever received one genuine, validly-signed webhook body from Shopify (as happens automatically and legitimately for every shop that installs the app) can resubmit that same raw body and HMAC value to the app's public webhook endpoint with a different `shopify-shop-domain` (and/or `shopify-topic`) header, and `Utils::HmacValidator.validate` will still return `true`, since it never examines those headers.

### Impact Explanation
This crosses the tenant boundary the gem is meant to enforce: webhook processing is documented and designed so the `shop` field in `WebhookMetadata` identifies which merchant's data is being delivered, and apps commonly key their per-tenant business logic (order/customer/product updates, uninstall/GDPR handling, etc.) off `data.shop`. Because `shop` is unauthenticated, an attacker who can obtain any single valid `(body, hmac)` pair — trivially available to them as a legitimate shop that installed the app and receives real webhooks — can attribute that (and only that) body to an arbitrary victim shop, causing the app to create, update, or delete tenant-scoped records for a shop the attacker does not control. This matches the "cross-tenant access" Critical impact category.

### Likelihood Explanation
The webhook HTTP endpoint is inherently public/unauthenticated by design (that's how Shopify itself reaches it), so any unprivileged internet user who is also a legitimate (even trial) merchant of the app can obtain one authentic `(raw_body, hmac)` pair for their own shop by simply triggering an event Shopify will webhook about, then replay it directly to the app's endpoint with a forged `shopify-shop-domain`/`shopify-topic` header. No access token, `client_secret`, or privileged account is required — the attacker never needs to know `api_secret_key` because they reuse a signature Shopify itself already produced for legitimate traffic.

### Recommendation
Include `shop`, `topic`, `webhook_id`, and `api_version` (or at minimum `shop` and `topic`) in the HMAC-covered signable content, or otherwise cryptographically bind them to the verified body (e.g. verify them against a value looked up from Shopify's API using the webhook_id, or require they match values in a trusted registration record) before constructing `WebhookMetadata`. At minimum, document clearly that `request.shop`/`request.topic` are unauthenticated and must not be trusted as tenant identifiers without an independent check (e.g. confirming the shop has an active, matching session/installation).

### Proof of Concept
1. Attacker installs the app on their own shop `attacker-shop.myshopify.com` (any unprivileged Shopify merchant account) and configures a webhook topic the app registers, e.g. `orders/create`.
2. Attacker performs the triggering action (e.g. creates an order in their own store), causing Shopify to POST a genuine, validly-HMAC-signed webhook to the app's public webhook endpoint, e.g.:
   ```
   POST /callback/orders/create
   X-Shopify-Topic: orders/create
   X-Shopify-Hmac-Sha256: <valid HMAC over raw_body>
   X-Shopify-Shop-Domain: attacker-shop.myshopify.com
   <raw_body containing order JSON, some fields of which attacker fully controls, e.g. note/tags>
   ```
3. Attacker intercepts/replays this exact same `raw_body` and `X-Shopify-Hmac-Sha256` value directly to the same endpoint, but changes the header:
   ```
   X-Shopify-Shop-Domain: victim-shop.myshopify.com
   ```
4. `Utils::HmacValidator.validate(request)` recomputes the HMAC over `to_signable_string` (`@raw_body` only) and it still matches, since the header change does not affect `@raw_body`. [7](#0-6) 
5. `Registry.process` proceeds and calls the handler with `WebhookMetadata.new(shop: "victim-shop.myshopify.com", body: <attacker's order JSON>, ...)`, so the app processes attacker-controlled webhook data attributed to `victim-shop.myshopify.com` — data the app believes came from the victim's tenant. [2](#0-1)

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L20-38)
```ruby
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

**File:** lib/shopify_api/webhooks/webhook_handler.rb (L6-12)
```ruby
    class WebhookMetadata < T::Struct
      const :topic, String
      const :shop, String
      const :body, T::Hash[String, T.untyped]
      const :api_version, String
      const :webhook_id, String
    end
```
