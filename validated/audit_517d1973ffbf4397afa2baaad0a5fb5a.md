### Title
Webhook Shop/Topic Identity Spoofing via Unauthenticated Headers Not Covered by HMAC - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` treats a webhook as authentic once `Utils::HmacValidator.validate(request)` succeeds, but the HMAC signature only covers the raw request body — never the `shop`, `topic`, or `webhook_id` values that the gem hands to the app's handler as the tenant/routing identity. Any request whose body+HMAC pair was legitimately issued by Shopify for one shop can be replayed with a forged `shopify-shop-domain` (and/or `shopify-topic`) header against the same endpoint, and it will pass validation while being attributed to a different, arbitrary shop.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`shop`, `topic`, and `webhook_id` are read straight from HTTP headers with no cryptographic binding to the signed body: [2](#0-1) 

`Registry.process` validates only that the body's HMAC matches (`Utils::HmacValidator.validate(request)`), then immediately forwards the unauthenticated `request.shop` and `request.topic` to the registered handler as the tenant-identifying metadata: [3](#0-2) 

`HmacValidator.validate` itself only ever calls `verifiable_query.to_signable_string`, i.e. the body, never the headers: [4](#0-3) 

The equality the gem's documentation implies should hold is:

`shop_used_for_tenant_routing (header) == shop_cryptographically_bound_by_HMAC (body)`

But in reality:

`shop_used_for_tenant_routing = unauthenticated header value`, which is never checked against anything HMAC-bound.

The gem's own documentation for `Registry.process` states that it "will verify the request did indeed come from Shopify" before invoking the handler, which is misleading — it only verifies the body's authenticity, not the shop/topic used to route that body: [5](#0-4) 

### Impact Explanation
Because the webhook signing secret (`Context.api_secret_key`) is shared across every shop that has the app installed, any merchant who installs the app can legitimately receive real, correctly-signed webhook deliveries for their own store. That merchant can then replay the exact body+`shopify-hmac-sha256` pair to the app's public webhook endpoint while substituting the `shopify-shop-domain` (and/or `shopify-topic`) header with a victim shop's domain. `HmacValidator.validate` still succeeds (it only checks the body), and `Registry.process` passes the forged shop/topic straight into `WebhookMetadata` and the app's handler: [6](#0-5) 

Any host application that trusts `data.shop`/`data.topic` from the handler callback for tenant-scoped writes (e.g. updating billing state, syncing orders, or processing GDPR-mandatory `customers/redact`/`shop/redact` topics) can be tricked into applying attacker-controlled data under a victim tenant's identity — a cross-tenant access condition.

### Likelihood Explanation
Exploitation requires no privileged credentials, no access token, and no knowledge of `api_secret_key`. It only requires the attacker to be a normal (unprivileged) merchant who has installed the app and can capture one of their own legitimately signed webhook deliveries (trivial, since they control the endpoint or can intercept their own HTTP traffic), then replay that request with a modified `shop-domain` header at the shared public webhook endpoint.

### Recommendation
Bind the `shop` (and ideally `topic`/`webhook_id`) values into the HMAC-signed content, or otherwise cryptographically verify that the shop asserted in the headers matches a shop the app actually expects/has an active session for, before invoking the handler. At minimum, `Registry.process` should require callers to supply and validate an expected shop list, and the gem's documentation should not claim that `process` fully "verifies the request did indeed come from Shopify" when only the body is covered.

### Proof of Concept
1. Attacker installs the app on `attacker-shop.myshopify.com` and lets Shopify deliver a legitimate webhook, e.g. for topic `customers/data_request`:
   ```
   POST /callback/customers/data_request
   shopify-topic: customers/data_request
   shopify-hmac-sha256: <valid HMAC of body B>
   shopify-shop-domain: attacker-shop.myshopify.com
   Body: B
   ```
2. Attacker resends the identical body `B` and identical `shopify-hmac-sha256` to the same endpoint, but changes the header:
   ```
   shopify-shop-domain: victim-shop.myshopify.com
   ```
3. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which only re-computes the HMAC over `B` — validation succeeds.
4. The handler is invoked with `WebhookMetadata.new(topic: ..., shop: "victim-shop.myshopify.com", body: <parsed B>, ...)`, so the host application processes attacker-controlled data as if it originated from `victim-shop.myshopify.com`.

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

**File:** lib/shopify_api/webhooks/request.rb (L35-43)
```ruby
      sig { override.returns(String) }
      def to_signable_string
        @raw_body
      end

      sig { returns(T::Hash[String, T.untyped]) }
      def parsed_body
        JSON.parse(@raw_body)
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
