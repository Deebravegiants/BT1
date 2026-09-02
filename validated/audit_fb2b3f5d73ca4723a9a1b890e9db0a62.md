### Title
Webhook shop-domain (and topic) identity is not covered by the HMAC signature, enabling cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` only returns the raw request body, while the `shop` (and `topic`) values that the framework treats as authenticated tenant-identifying fields are taken from HTTP headers that are excluded from the HMAC computation.

### Finding Description
`ShopifyAPI::Webhooks::Registry.process` validates a webhook solely via `Utils::HmacValidator.validate(request)`, which computes the signature over `request.to_signable_string`: [1](#0-0) 

`to_signable_string` returns only `@raw_body`: [2](#0-1) 

But `shop` and `topic` — the very fields the registry uses to route the payload and identify the tenant — are pulled from the `shopify-shop-domain`/`x-shopify-shop-domain` and `shopify-topic`/`x-shopify-topic` headers, which are never part of the signed bytes: [3](#0-2) 

After HMAC validation passes, `process` builds `WebhookMetadata` directly from `request.shop` and `request.topic` and hands it to the app's `WebhookHandler`: [4](#0-3) 

`WebhookMetadata.shop` is a `const :shop, String` field that host applications use to determine which merchant/tenant the webhook body applies to: [5](#0-4) 

This breaks the intended binding `signed_bytes == (body, shop, topic)` down to `signed_bytes == (body)`. Because Shopify signs all webhooks for an app with the same shared `client_secret` regardless of which installed shop triggered the event, an unprivileged internet user who owns/controls their own shop installation of the app can:
1. Install the target app on their own (attacker-controlled) shop and trigger a webhook whose body they control (e.g., by editing a product to a chosen title/price, or via any webhook topic whose payload content is attacker-influenced).
2. Receive the resulting webhook HTTP request, which carries a **valid** HMAC (computed over the raw body only, using the app's shared secret) alongside `X-Shopify-Shop-Domain: attacker-shop.myshopify.com`.
3. Replay that exact body + HMAC to the app's webhook endpoint while substituting `X-Shopify-Shop-Domain` with a victim's shop domain (and/or a different `X-Shopify-Topic`). `HmacValidator.validate` still succeeds because the signature check ignores these headers entirely.
4. The registry then dispatches `WebhookMetadata.new(topic: <attacker-chosen>, shop: <victim-shop>, body: <attacker-controlled>, ...)` to the host app's handler, which will process attacker-controlled data as if it originated from the victim's shop.

### Impact Explanation
This is a cross-tenant data-injection vector: the gem lets an attacker who is merely a merchant/installer of the target app forge webhook events attributed to any other shop, with attacker-controlled body content, because the identity fields consumed by the handler (`shop`, `topic`) are not cryptographically bound to the signed payload. Depending on how the host app's `WebhookHandler#handle` uses `data.shop` (e.g., to look up/act on that shop's stored session or resources), this can result in cross-tenant access/mutation of another merchant's data — matching the Critical "cross-tenant access" impact category.

### Likelihood Explanation
The attacker only needs an ordinary, unprivileged install of the app on a shop they control (or the ability to observe a webhook sent to any shop using the app, since the shared secret makes all HMACs universally valid across shops) and the ability to POST an HTTP request to the app's public webhook endpoint with modified headers and the previously captured valid body+HMAC pair — no access token, `client_secret`, or privileged account is required.

### Recommendation
Include the tenant-identifying headers (`shop-domain`, and ideally `topic`, `webhook-id`, `api-version`) in the HMAC-signed material, or otherwise cryptographically bind them to the payload before trusting them in `WebhookMetadata`. At minimum, `Request#to_signable_string` should incorporate the shop domain so that `HmacValidator.validate` fails whenever an attacker substitutes a different shop's identity while reusing a validly-signed body.

### Proof of Concept
```ruby
# Attacker installs the app on their own shop "attacker-shop.myshopify.com"
# and triggers a webhook whose body they control, e.g. products/update.
# Shopify sends (legitimately, with a VALID hmac computed over the raw body only):
#
#   X-Shopify-Topic: products/update
#   X-Shopify-Hmac-Sha256: <valid HMAC of RAW_BODY using app's shared client_secret>
#   X-Shopify-Shop-Domain: attacker-shop.myshopify.com
#   Body: RAW_BODY  (attacker-controlled content)

# Attacker replays the SAME raw body and SAME valid hmac, but swaps only the
# shop-domain header to a victim shop that also has the app installed:
headers = {
  "x-shopify-topic" => "products/update",
  "x-shopify-hmac-sha256" => captured_valid_hmac,     # unchanged, still valid
  "x-shopify-shop-domain" => "victim-shop.myshopify.com", # forged
}

request = ShopifyAPI::Webhooks::Request.new(raw_body: captured_raw_body, headers: headers)

# HmacValidator only checks raw_body against the shared secret -> passes.
ShopifyAPI::Webhooks::Registry.process(request)
# => handler.handle(data: WebhookMetadata.new(topic: "products/update",
#                                              shop: "victim-shop.myshopify.com",
#                                              body: attacker_controlled_body, ...))
```
`request.rb` lines 15-38 show `shop`/`topic` come from unsigned headers while `to_signable_string` (used by `HmacValidator`) covers only the body, confirming the header substitution above passes validation.

### Citations

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
