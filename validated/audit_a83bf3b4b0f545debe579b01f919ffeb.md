This confirms the finding: the docs explicitly state `Registry.process` "will verify the request did indeed come from Shopify" (docs/usage/webhooks.md:125), but the verified bytes (`Request#to_signable_string` returning only `@raw_body`) never include the `shop`, `topic`, or `webhook_id` headers that `Registry.process`/`WebhookMetadata` hand to the app's trusted handler.

### Title
Webhook `shop` (and `topic`/`webhook_id`) identity is trusted from unauthenticated headers while only the raw body is HMAC-verified, enabling cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`, `lib/shopify_api/webhooks/registry.rb`)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`, so `Utils::HmacValidator.validate` (used by `Registry.process`) authenticates nothing but the request body bytes. The `shop-domain`, `topic`, and `webhook-id` headers, which `Registry.process` extracts and forwards to the app's `WebhookHandler` as trusted `WebhookMetadata`, are never bound to that signature. An attacker who is a legitimate (even if malicious) merchant on their own shop can capture one genuine webhook delivery for their shop (valid body + valid HMAC, since Shopify apps typically use a single shared `client_secret` across all installed shops), then replay that exact body/HMAC pair to the app's webhook endpoint with a forged `X-Shopify-Shop-Domain` header naming a victim shop. The HMAC still validates (it only covers the body), and the app processes attacker-controlled event data as if it originated from the victim tenant.

### Finding Description
- `lib/shopify_api/webhooks/request.rb:35-38` — `to_signable_string` returns `@raw_body` only: [1](#0-0) 
- `shop`, `topic`, and `webhook_id` are read straight from attacker-controllable HTTP headers with no cross-check against the signature: [2](#0-1) 
- `Registry.process` only calls `Utils::HmacValidator.validate(request)` (body-only check) before trusting `request.shop`/`request.topic`/`request.webhook_id` and handing them to the app's handler: [3](#0-2) 
- `Utils::HmacValidator.validate` computes the signature purely from `verifiable_query.to_signable_string`, i.e., the body for webhooks: [4](#0-3) 
- The gem's own documentation explicitly tells integrators that `Registry.process` "will verify the request did indeed come from Shopify," implying the whole request (including shop identity) is authenticated — which it is not: [5](#0-4) 
- `WebhookMetadata.shop` is then handed to the handler as trusted tenant identity, matching the documented contract ("`shop`, `String` - The shop domain of the webhook"): [6](#0-5) 

The broken identity binding, stated as an equality: `shop_bytes_covered_by_HMAC` (empty set — only `raw_body` is signed) `!=` `shop_bytes_trusted_by_handler` (`request.shop`, taken from the `X-Shopify-Shop-Domain` header and delivered via `WebhookMetadata#shop`). Nothing in this gem ties the header-derived shop to the HMAC-verified payload, so any request bearing a body/HMAC pair valid for the app's shared `client_secret` will be accepted regardless of which shop's header accompanies it.

### Impact Explanation
This is a cross-tenant access vulnerability: an unprivileged internet user who is merely a legitimate merchant/installer of the app on their own shop can forge webhook deliveries attributed to a completely different, victim shop. Depending on the app's handler logic (as shown in the gem's own docs, handlers commonly enqueue jobs keyed by `data.shop`), this can inject falsified data (fake orders, product updates, `app/uninstalled`, or the mandatory GDPR topics `shop/redact`, `customers/redact`, `customers/data_request`) into a victim tenant's records, corrupt per-shop billing/usage accounting, or trigger data-deletion workflows for a shop the attacker does not control. This matches the mandated Critical impact category "cross-tenant access."

### Likelihood Explanation
Likelihood is high for any multi-tenant Shopify app (the common case) that shares one `client_secret` across all shop installations — which is the standard OAuth model this same gem implements. The attacker only needs to install the target app on their own shop, capture one legitimate webhook, and replay it with a modified `Shop-Domain` header to their app's public webhook endpoint. No access token, secret, or privileged account is required beyond the attacker's own ordinary merchant account.

### Recommendation
Bind the trusted request metadata to the HMAC. At minimum:
1. Include `shop-domain`, `topic`, and `webhook-id` header values in the signable string used by `Webhooks::Request#to_signable_string`, matching what Shopify itself computes, or
2. If Shopify's HMAC scheme is genuinely body-only (as documented by Shopify), require callers to separately validate the delivering shop is one that the app has an active session/installation for (cross-check `request.shop` against known installed shops) before trusting `WebhookMetadata#shop`, and clearly document that `Registry.process`'s HMAC check does not authenticate the shop/topic headers.

### Proof of Concept
1. App has a shared `client_secret` for all shop installations (default Shopify OAuth model).
2. Attacker installs the app on `attacker-shop.myshopify.com` and receives a real webhook, e.g., topic `carts/update`, body `{"id":1}`, with headers:
   - `x-shopify-hmac-sha256: <valid HMAC of the body>`
   - `x-shopify-shop-domain: attacker-shop.myshopify.com`
   - `x-shopify-topic: carts/update`
3. Attacker replays the exact same body and `x-shopify-hmac-sha256` value to the app's public webhook endpoint, but sets:
   - `x-shopify-shop-domain: victim-shop.myshopify.com`
4. `ShopifyAPI::Webhooks::Request.new` accepts the forged headers (`lib/shopify_api/webhooks/request.rb:45-63`), and `Utils::HmacValidator.validate` succeeds because it only hashes `@raw_body` (`lib/shopify_api/webhooks/request.rb:36-38`, `lib/shopify_api/utils/hmac_validator.rb:26-31`).
5. `Registry.process` calls the app's handler with `WebhookMetadata.new(shop: "victim-shop.myshopify.com", topic: "carts/update", body: {"id"=>1}, ...)` (`lib/shopify_api/webhooks/registry.rb:198-199`), and the app processes attacker-supplied data as though it were an authentic event from the victim tenant.

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

**File:** docs/usage/webhooks.md (L123-136)
```markdown
## Process a Webhook

To process an http webhook, you need to listen on the route(s) you provided during the Webhook registration process, then when the route is hit construct a `ShopifyAPI::Webhooks::Request` and call `ShopifyAPI::Webhooks::Registry.process`. This will verify the request did indeed come from Shopify and then call the specified handler for that webhook. An example in Rails is shown below:

```ruby
class WebhookController < ApplicationController
  def webhook
    ShopifyAPI::Webhooks::Registry.process(
      ShopifyAPI::Webhooks::Request.new(raw_body: request.raw_post, headers: request.headers.to_h)
    )
    render json: {success: true}.to_json
  end
end
```
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
