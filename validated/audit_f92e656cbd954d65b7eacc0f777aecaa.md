### Title
Webhook shop-domain header is not covered by HMAC verification, enabling cross-tenant webhook spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an inbound webhook solely by validating that `hmac(secret, raw_body)` matches the `x-shopify-hmac-sha256` header. However, the `shop` (from `x-shopify-shop-domain`), `topic`, `webhook-id`, and `api-version` headers used to route and attribute the webhook are never included in the HMAC-signed material, breaking the binding `shop authenticated == shop the payload is attributed to`.

### Finding Description
`Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`Utils::HmacValidator.validate` computes the HMAC exclusively over that signable string and compares it to the `hmac` header: [2](#0-1) 

`Registry.process` treats a passing HMAC check as full authentication of the request, then immediately trusts `request.shop`, `request.topic`, and `request.webhook_id` — none of which were part of the signed bytes — to build `WebhookMetadata` and dispatch to the app's handler: [3](#0-2) 

`Request#shop`, `#topic`, and `#webhook_id` are all pulled straight from unauthenticated headers: [4](#0-3) 

Because the `x-shopify-shop-domain` header sits outside the HMAC's coverage, the equality the app relies on — "HMAC-verified sender == shop attributed to this webhook" — does not actually hold. Any principal who has captured one legitimately-signed `(raw_body, hmac)` pair (trivial to obtain, since an attacker can register their own Shopify dev/trial store and receive real webhooks for it, which are signed with the same `api_secret_key` for every shop the app serves) can replay that exact body/HMAC pair to the app's public webhook endpoint while substituting an arbitrary `x-shopify-shop-domain` value. `HmacValidator.validate` will still pass (it never looks at the shop header), and `Registry.process` will hand the attacker-supplied body to the app's handler tagged with a victim shop's domain — a cross-tenant payload injection.

### Impact Explanation
This is a Critical-tier cross-tenant issue: because the app-level `api_secret_key` is shared across all merchants of an app, and the HMAC only binds the body, an attacker can make the app process attacker-chosen webhook data (e.g. an `orders/create` or `app/uninstalled` payload) under the identity of a different, victim shop. Depending on how the host app's handler uses `WebhookMetadata#shop` (typically to look up/update the merchant's local record), this can lead to cross-tenant data corruption, spoofed uninstall/GDPR events, or state confusion between tenants — all without possessing the victim's access token or any privileged credential.

### Likelihood Explanation
Exploitation requires only: (1) the attacker's own legitimate app installation (trivial — attacker installs the same public app on their own store), (2) capturing one real webhook delivery (a passive network observer position or simply their own webhook receiver logs, since they are the legitimate recipient), and (3) resending it to the app's public webhook endpoint with a modified `x-shopify-shop-domain`/`x-shopify-topic` header. No secrets beyond what a normal, unprivileged merchant already has access to are needed, and the webhook endpoint is by design internet-reachable and unauthenticated apart from the HMAC.

### Recommendation
Bind the routing/attribution headers into the authenticated material, e.g. include `shop`, `topic`, and `webhook_id` in the HMAC-signed string (or otherwise cryptographically bind them), or at minimum require the caller to independently confirm that the `shop-domain` in the request corresponds to a shop with an active session/installation known to the app before dispatching to a handler. Shopify's own webhook signing does not currently sign headers, so the safer mitigation within this gem is to document/require host applications to cross-check `WebhookMetadata#shop` against their own installed-shop registry before trusting the payload, and to consider deriving a combined digest over `topic + shop + raw_body` if the API surface allows evolving the signature scheme.

### Proof of Concept
```ruby
# 1. Attacker installs the same app on their own shop "attacker.myshopify.com"
#    and receives a real, validly-signed webhook, e.g. orders/create:
raw_body = '{"id":1,"malicious":"payload"}'
hmac = OpenSSL::HMAC.digest(OpenSSL::Digest.new("sha256"), api_secret_key, raw_body)
headers = {
  "x-shopify-topic" => "orders/create",
  "x-shopify-hmac-sha256" => Base64.encode64(hmac),
  "x-shopify-shop-domain" => "attacker.myshopify.com", # original, legitimate
}
# This request passes HmacValidator.validate and is processed normally.

# 2. Attacker replays the identical (raw_body, hmac) pair but swaps the shop header
#    to a victim shop they do not control:
forged_headers = headers.merge("x-shopify-shop-domain" => "victim-shop.myshopify.com")
request = ShopifyAPI::Webhooks::Request.new(raw_body: raw_body, headers: forged_headers)

# HmacValidator.validate(request) still returns true, because it only hashes raw_body.
ShopifyAPI::Webhooks::Registry.process(request)
# => the app's handler is invoked with WebhookMetadata(shop: "victim-shop.myshopify.com", ...)
#    even though the payload never originated from Shopify for that shop.
``` [3](#0-2) [5](#0-4)

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L10-33)
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
