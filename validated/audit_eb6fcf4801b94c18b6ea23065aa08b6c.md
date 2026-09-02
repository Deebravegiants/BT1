### Title
Webhook `shop-domain` and `topic` headers are trusted for routing/attribution without being covered by the HMAC signature - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Utils::HmacValidator.validate` only authenticates the raw HTTP body of an incoming webhook. The `shop-domain` and `topic` values that the gem uses to attribute and dispatch the webhook are read from unauthenticated HTTP headers, so an attacker who possesses one valid `(body, hmac)` pair can replay it with arbitrary `shop-domain`/`topic` headers and still pass verification.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`ShopifyAPI::Utils::HmacValidator.validate` computes/compares the signature exclusively against `verifiable_query.to_signable_string`: [2](#0-1) 

`shop`, `topic`, and `webhook_id` are all pulled straight from HTTP headers, none of which participate in `to_signable_string`: [3](#0-2) 

`ShopifyAPI::Webhooks::Registry.process` then uses these unauthenticated header values as the sole basis for both routing (`@registry[request.topic]`) and shop attribution (`WebhookMetadata.new(shop: request.shop, ...)`): [4](#0-3) 

The identity binding the gem implicitly claims to provide is:
`HMAC-authenticated bytes == (shop, topic) used for dispatch/attribution`

In reality the equality does not hold: only the raw body bytes are authenticated; `shop` and `topic` are parsed from headers that sit entirely outside the signed content. Because the app's `api_secret_key` is shared across every shop that installs the app, any party who can obtain one legitimate `(body, hmac)` pair for that app — e.g., by installing the app on their own store and capturing a real webhook delivery — can resend that exact body/HMAC to the app's public webhook endpoint while substituting the `x-shopify-shop-domain` header for a victim shop's domain (and/or the `x-shopify-topic` header for a different topic). `HmacValidator.validate` will still return `true`, because it never inspected those headers, and `Registry.process` will hand the attacker-controlled body to the handler tagged with the victim's `shop` (and/or under a different topic than the one the payload actually represents).

### Impact Explanation
This breaks the tenant boundary that host applications rely on this gem to enforce: a webhook the gem certifies as "valid and from shop X" can actually be attacker-supplied content attributed to any shop the attacker chooses, and/or misrouted to a different handler than the body's real topic. Any host application that uses `WebhookMetadata#shop` (as returned by this gem) to select which merchant's session/data to update will act on forged content under a victim shop's identity — this is cross-tenant data injection/impersonation through this gem's own webhook-validation API, not misuse of a documented contract.

### Likelihood Explanation
Requires no privileged access: any internet user can install the target app for free on their own development/test store, capture one legitimate webhook body+HMAC, and replay it to the app's public webhook URL with forged shop/topic headers. `Registry.process`/`HmacValidator.validate` provide no signal that would reject the forged headers.

### Recommendation
Bind `shop-domain`, `topic`, and `webhook-id` into the signed material verified by `HmacValidator` (e.g., verify them as part of the canonical string, or require the caller to independently confirm the `shop` header matches an existing, previously-authenticated session/install record before trusting it), and treat header-derived metadata as untrusted until it is cross-checked against data obtained through an authenticated channel (e.g., the shop that installed the app and holds a matching access token).

### Proof of Concept
```ruby
# Attacker installs the target app on their own shop "attacker.myshopify.com"
# and captures a legitimate webhook delivery:
real_body = '{"id": 1, "note": "hello"}'
real_hmac = OpenSSL::HMAC.digest(OpenSSL::Digest.new("sha256"), app_secret, real_body)

# Attacker replays the SAME body+hmac to the app's public webhook endpoint,
# but swaps the shop-domain header to a victim store:
forged_headers = {
  "x-shopify-topic" => "orders/create",
  "x-shopify-hmac-sha256" => Base64.encode64(real_hmac),
  "x-shopify-shop-domain" => "victim-shop.myshopify.com", # forged, unauthenticated
}

request = ShopifyAPI::Webhooks::Request.new(raw_body: real_body, headers: forged_headers)
ShopifyAPI::Webhooks::Registry.process(request)
# HmacValidator.validate(request) => true, because only `real_body` is checked.
# The registered handler receives WebhookMetadata(shop: "victim-shop.myshopify.com", ...)
# even though the body/HMAC actually originated from the attacker's own shop.
```

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
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
