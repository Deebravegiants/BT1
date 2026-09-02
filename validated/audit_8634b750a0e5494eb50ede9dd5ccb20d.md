### Title
Webhook shop/topic identity headers are not covered by the HMAC, enabling cross-tenant webhook forgery - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw HTTP body, while the `shop`, `topic`, `api_version`, and `webhook_id` values are read straight from unauthenticated request headers. `ShopifyAPI::Webhooks::Registry.process` trusts these header-derived values (in particular `request.shop`) to build the `WebhookMetadata` passed to the host app's handler, after checking only that the HMAC of the body is valid.

### Finding Description
The identity binding that should hold is: `shop asserted to the handler == shop that the HMAC-signed body actually originated from`. Instead the code enforces only `hmac(body, client_secret) == received_hmac`, and separately reads `shop` (and `topic`, `webhook_id`, `api_version`) from headers that are never mixed into the signed material: [1](#0-0) 

```ruby
def hmac
  Digest.hexencode(Base64.decode64(T.cast(shopify_header("hmac-sha256"), String)))
end
...
def shop
  T.cast(shopify_header("shop-domain"), String)
end
...
def to_signable_string
  @raw_body
end
``` [1](#0-0) 

`Registry.process` then validates only the body/HMAC pair and forwards the attacker-controllable `shop` header verbatim to the app's handler: [2](#0-1) 

Because the client_secret used to sign webhooks is shared across *every* shop that has the app installed, an unprivileged internet user can install the target app on a shop they control (e.g., a free/dev store), receive a legitimately HMAC-signed webhook (valid `raw_body` + `hmac-sha256` pair for their own shop), and then replay that exact `(raw_body, hmac)` pair to the app's webhook endpoint while substituting the `x-shopify-shop-domain` (and/or `x-shopify-topic`, `x-shopify-webhook-id`) header with a victim shop's domain. `HmacValidator.validate` only recomputes the HMAC over `raw_body`, so it still succeeds, and `Registry.process` calls the host app's handler with `WebhookMetadata#shop` equal to the attacker-chosen victim domain instead of the shop that actually produced the signed body.

### Impact Explanation
This breaks the tenant boundary that webhook processing is supposed to enforce: `data.shop` in `WebhookMetadata` (used by host apps to select which tenant's session/record to act on) can be forged to any shop domain while still passing signature verification, since `shop` is never part of the signed payload. Any host application logic that trusts `WebhookMetadata#shop` to identify the shop whose data should be created/updated/deleted (a documented and expected usage pattern of this gem) can be tricked into acting as if the attacker's payload belongs to a shop the attacker does not control — a cross-tenant access impact.

### Likelihood Explanation
Exploitation requires only: (1) installing the target app on any shop (including a free/dev shop, no special privilege needed), (2) capturing one legitimate webhook delivery, and (3) replaying it with a modified `shop-domain`/`topic` header to the app's public webhook endpoint. No access to the app's `client_secret`, access tokens, or any privileged account is required.

### Recommendation
Include the identity-bearing headers (`shop-domain`, `topic`, `webhook-id`, `api-version`) in the signable material used by `HmacValidator`, or otherwise cryptographically bind them to the body (e.g., verify `shop` against a value derived from a trusted, signed source such as the JWT `dest` claim rather than an unauthenticated header) before constructing `WebhookMetadata` in `ShopifyAPI::Webhooks::Registry.process`.

### Proof of Concept
1. Attacker creates/uses shop `attacker.myshopify.com` and installs the vulnerable app, causing Shopify to deliver a legitimate webhook (e.g. `orders/create`) to the app's endpoint with headers:
   ```
   x-shopify-topic: orders/create
   x-shopify-hmac-sha256: <valid HMAC of raw_body>
   x-shopify-shop-domain: attacker.myshopify.com
   ```
2. Attacker captures the exact `raw_body` and `x-shopify-hmac-sha256` value.
3. Attacker sends a new HTTP request to the same app webhook endpoint, reusing the identical `raw_body` and `x-shopify-hmac-sha256`, but with:
   ```
   x-shopify-shop-domain: victim-shop.myshopify.com
   ```
4. `ShopifyAPI::Webhooks::Request.new` accepts the forged headers, `Utils::HmacValidator.validate(request)` succeeds (body/HMAC unchanged), and `Registry.process` invokes the app's handler with `WebhookMetadata.new(shop: "victim-shop.myshopify.com", ...)`, causing the app to process attacker-controlled data as if it belonged to `victim-shop.myshopify.com`.

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
