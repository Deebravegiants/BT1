Confirmed. This confirms the vulnerable identity binding: `Webhooks::Request#to_signable_string` returns only `@raw_body` [1](#0-0)  while `shop`, `topic`, and `webhook_id` are pulled straight from unauthenticated HTTP headers [2](#0-1) , and `Registry.process` only checks `Utils::HmacValidator.validate(request)` (which hashes `to_signable_string`, i.e., body only) before handing `request.shop` to the app's handler as an authenticated tenant identifier [3](#0-2) .

### Title
Webhook shop-domain identity spoofing via HMAC/body-only signature binding - (File: lib/shopify_api/webhooks/request.rb, lib/shopify_api/webhooks/registry.rb)

### Summary
`ShopifyAPI::Webhooks::Registry.process` is documented to "verify the request did indeed come from Shopify" before invoking the app's handler with `data.shop` as "The shop domain of the webhook" [4](#0-3) . In reality, the HMAC signature only covers the raw request body — `Request#to_signable_string` returns `@raw_body` [1](#0-0)  — while `shop`, `topic`, and `webhook_id` are read verbatim from HTTP headers that are never included in the signed bytes [2](#0-1) . `HmacValidator.validate` only recomputes and compares the HMAC over `to_signable_string` [5](#0-4) , so a body+HMAC pair that is valid for one shop is equally "valid" no matter what `shop-domain` header accompanies it.

### Finding Description
The gem verifies "bytes signed" (the body) but the application-level identity binding it hands to the app — `data.shop` used for tenant scoping in `WebhookMetadata` — is "bytes parsed" from an unauthenticated header, not the field verified by the HMAC. This is the same class of bug as the FenwickTree example: an operation is performed against one identifier (the header-derived `shop`) while the security check (HMAC) was computed over something else (the body only), so the two are silently decoupled. `Registry.process` never cross-checks that the body's content is bound to the claimed `shop-domain` header [6](#0-5) .

### Impact Explanation
Because the app's `api_secret_key` is the same across every shop that installs the app, any unprivileged user who can trigger a real webhook delivery for their *own* shop (e.g., by placing a test order to trigger `orders/create`) obtains a body+HMAC pair that is cryptographically valid under the app's secret. That attacker can then POST this captured `(body, hmac)` directly to the app's public webhook endpoint while substituting an arbitrary `X-Shopify-Shop-Domain` header naming a victim shop. `Registry.process` validates the HMAC successfully (it only checks the body) and dispatches the handler with `data.shop` set to the victim's domain, causing the app to ingest attacker-controlled data as if it belonged to the victim tenant — a cross-tenant data-integrity/confusion issue reachable by any unprivileged internet user with no access token, no `client_secret`, and no privileged account.

### Likelihood Explanation
Any merchant/developer (including a free-trial or test account) can install the target app on their own store and trigger arbitrary webhook topics for that store, giving them a valid `(body, hmac)` pair at will. The webhook HTTP endpoint is by design internet-reachable and unauthenticated aside from the HMAC check, so replaying the captured request with a forged shop header requires only a basic HTTP client — no credential theft, no TLS interception, no social engineering.

### Recommendation
Bind the shop identity into the verified payload instead of trusting the header independently: e.g., require handlers/apps to cross-check `request.shop` against a shop already known to be associated with `webhook_id`/topic via the app's own session store, or extend `to_signable_string` / a companion check so the header-derived shop is confirmed against Shopify's registered webhook subscription (e.g., look up the webhook by `webhook_id` via the Admin API for the claimed shop before trusting `data.shop`) rather than accepting it as authenticated solely because the *body* HMAC matched.

### Proof of Concept
```ruby
# 1. Attacker installs the target app on their own shop "attacker-shop.myshopify.com"
#    and triggers, e.g., an orders/create webhook, capturing:
raw_body = capture_raw_body_from_own_webhook_delivery
hmac_b64 = capture_hmac_header_from_own_webhook_delivery # valid for app's api_secret_key + raw_body

# 2. Attacker crafts a forged request to the app's public webhook endpoint,
#    keeping the same body/hmac (still verifies) but swapping the shop header:
forged_headers = {
  "x-shopify-topic" => "orders/create",
  "x-shopify-hmac-sha256" => hmac_b64,
  "x-shopify-shop-domain" => "victim-shop.myshopify.com", # not covered by HMAC
  "x-shopify-webhook-id" => "attacker-chosen-id",
  "x-shopify-api-version" => "2024-01",
}

request = ShopifyAPI::Webhooks::Request.new(raw_body: raw_body, headers: forged_headers)
ShopifyAPI::Webhooks::Registry.process(request)
# => HmacValidator.validate(request) returns true (only raw_body is checked)
# => handler.handle(data: WebhookMetadata.new(shop: "victim-shop.myshopify.com", ...))
# The app now processes attacker-controlled order data attributed to victim-shop.
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
