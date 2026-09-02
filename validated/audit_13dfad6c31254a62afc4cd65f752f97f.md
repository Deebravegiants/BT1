## Title
Webhook `shop` identity is not covered by the HMAC signature, enabling cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC over the raw request body only, while the `shop` (tenant identity), `topic`, and `webhook_id` values used by `ShopifyAPI::Webhooks::Registry.process` are read from unauthenticated HTTP headers that are never included in the signed material. This breaks the equality that should hold between "the shop the HMAC actually authenticates" and "the shop the handler is told the data belongs to," allowing an attacker who can obtain one validly-signed webhook (e.g., for their own shop) to relabel it as belonging to a different, victim shop.

### Finding Description
`Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

but `Request#shop`, `#topic`, and `#webhook_id` are all pulled directly from HTTP headers with no cryptographic binding to that signature: [2](#0-1) 

`Registry.process` validates only the HMAC over the body, then forwards the header-derived `shop` (and `topic`/`webhook_id`) straight to the app's handler as trusted `WebhookMetadata`: [3](#0-2) 

The library's own documentation confirms apps are expected to treat `data.shop` from `WebhookMetadata` as trustworthy shop identity once `Registry.process` succeeds: [4](#0-3) 

The broken identity binding, stated as an equality:
- Expected: `shop bound by HMAC == shop delivered to handler`
- Actual: `shop bound by HMAC (nothing, since only body is signed) != shop-domain header value trusted by handler`

**Attack sequence:**
1. Attacker signs up for a free/dev Shopify store and installs the victim app on `attacker-shop.myshopify.com` — no privileged credentials or `api_secret_key` needed.
2. Shopify sends a legitimately-signed webhook to the app's endpoint: valid `X-Shopify-Hmac-Sha256` (computed by Shopify using the app's real `client_secret`, which the attacker never sees) over a body the attacker fully controls (e.g., by editing product/order data in their own store before the webhook fires).
3. Attacker intercepts/replays this exact `raw_body` + `hmac` pair to the app's webhook endpoint, but substitutes the `X-Shopify-Shop-Domain` (and/or `X-Shopify-Topic`/`X-Shopify-Webhook-Id`) header with the victim shop's domain.
4. `Utils::HmacValidator.validate` in `HmacValidator#validate_signature` only recomputes the HMAC over `to_signable_string` (i.e., `@raw_body`) and compares it, so it still passes — headers were never part of the signed content.
5. `Registry.process` proceeds and calls the app's handler with `WebhookMetadata` claiming the (attacker-controlled) body belongs to the victim shop. [5](#0-4)  confirms the signature check is solely over `verifiable_query.to_signable_string`.

### Impact Explanation
Any host application that follows this gem's documented pattern (`Registry.process` → `WebhookMetadata.shop`) to route or tag data per-tenant will accept attacker-crafted body content as if it originated from an arbitrary victim shop, since the shop identity is never part of the cryptographically verified content. This is a cross-tenant data-integrity/confusion vulnerability: an unprivileged attacker (any developer who can install the app on their own store) can inject fabricated webhook payloads attributed to a shop they do not control.

### Likelihood Explanation
Any Shopify app developer or user can install the target app on a free/dev store to obtain one validly-signed webhook, then simply modify the `shop-domain` header (and matching topic/id headers as desired) on a replay — no secrets, tokens, or privileged access are required, and the vulnerable code path is exactly the one demonstrated as best practice in the gem's own documentation.

### Recommendation
Bind the shop (and ideally topic/webhook id) into the material verified by the HMAC, or otherwise cryptographically/independently verify that the `shop-domain` header corresponds to a shop for which this specific webhook body/HMAC pair was actually issued (e.g., cross-check against the shop's currently stored access-token/session before trusting `WebhookMetadata.shop`), rather than trusting it as a bare, unauthenticated header value.

### Proof of Concept
```ruby
require "openssl"

secret = ShopifyAPI::Context.api_secret_key
body = '{"id":1,"note":"hello"}'
hmac = OpenSSL::HMAC.digest(OpenSSL::Digest.new("sha256"), secret, body)

# Step 1: attacker captures a legitimately-signed webhook for THEIR OWN shop
legit_headers = {
  "shopify-topic" => "orders/create",
  "shopify-hmac-sha256" => Base64.encode64(hmac),
  "shopify-shop-domain" => "attacker-shop.myshopify.com",
  "shopify-webhook-id" => "attacker-generated-id",
  "shopify-api-version" => "2024-01",
}

# Step 2: attacker replays same body+hmac but swaps the shop header to the victim
spoofed_headers = legit_headers.merge("shopify-shop-domain" => "victim-shop.myshopify.com")

request = ShopifyAPI::Webhooks::Request.new(raw_body: body, headers: spoofed_headers)

# HMAC validation still succeeds because it only checks `body`, not headers:
ShopifyAPI::Utils::HmacValidator.validate(request) # => true

ShopifyAPI::Webhooks::Registry.process(request)
# handler.handle receives WebhookMetadata(shop: "victim-shop.myshopify.com", body: {"id"=>1,"note"=>"hello"}, ...)
# even though the data actually originated from attacker-shop.myshopify.com
```

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

**File:** docs/usage/webhooks.md (L10-18)
```markdown
If you want to register for an http webhook you need to implement a webhook handler which the `shopify_api` gem can use to determine how to process your webhook. You can make multiple implementations (one per topic) or you can make one implementation capable of handling all the topics you want to subscribe to. To do this simply make a module or class that includes or extends `ShopifyAPI::Webhooks::WebhookHandler` and implement the `handle` method which accepts the following named parameters: data: `WebhookMetadata`. An example implementation is shown below:

`data` will have the following keys
- `topic`, `String` - The topic of the webhook
- `shop`, `String` - The shop domain of the webhook
- `body`, `T::Hash[String, T.untyped]`- The body of the webhook
- `webhook_id`, `String` - The id of the webhook event to [avoid duplicates](https://shopify.dev/docs/apps/webhooks/best-practices#ignore-duplicates)
- `api_version`, `String` - The api version of the webhook

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
