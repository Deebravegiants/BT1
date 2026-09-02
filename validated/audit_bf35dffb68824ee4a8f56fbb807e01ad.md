This confirms the vulnerability: the gem's own documentation states `ShopifyAPI::Webhooks::Registry.process` "will verify the request did indeed come from Shopify" via `data.shop`, and instructs handlers to trust `data.shop` as the tenant identifier for routing/persisting data — but the identity binding is broken.

### Title
Webhook `shop` (and `topic`/`webhook_id`) identity fields are not covered by the HMAC signature, enabling cross-tenant webhook spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` derives the HMAC-verified bytes solely from the raw request body, while the `shop`, `topic`, `webhook_id`, and `api_version` fields used by `ShopifyAPI::Webhooks::Registry.process` to identify the tenant and route the payload are read from unauthenticated HTTP headers that are never included in the signed content.

### Finding Description
`Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`Request#shop` (and `topic`, `webhook_id`, `api_version`) are parsed straight from HTTP headers with no cryptographic binding to that value: [2](#0-1) 

`Registry.process` validates only the HMAC over the body, then immediately trusts `request.shop` as the tenant identity passed to the app's handler: [3](#0-2) 

`HmacValidator.validate` computes and compares the signature exclusively against `verifiable_query.to_signable_string`, i.e. the body only: [4](#0-3) 

The identity equality the system is supposed to enforce is:
`HMAC-verified bytes == bytes that determine the shop the payload is attributed to`

Here that equality is broken: `HMAC-verified bytes == raw_body`, but `shop-attribution bytes == shopify-shop-domain header`, which is disjoint from `raw_body`. The gem's own documentation instructs handlers to treat `data.shop` as verified and use it to route/persist data (e.g. `perform_later(topic: data.topic, shop_domain: data.shop, webhook: data.body)`), reinforcing that this header is expected to be trustworthy once `Registry.process` "verifies the request did indeed come from Shopify": [5](#0-4) 

Because the same `api_secret_key` is shared across all shops installed on a given app, any body+HMAC pair that is valid for one shop's webhook is also a valid HMAC for the identical body regardless of which `shop-domain` header accompanies it — the signature makes no statement about the shop. An attacker who can obtain one legitimate `(raw_body, X-Shopify-Hmac-Sha256)` pair delivered to their own webhook endpoint (e.g., by installing the target app on their own store, which requires no privileged credentials) can replay that exact body+HMAC to the app's webhook URL while substituting the `X-Shopify-Shop-Domain` header for a victim shop's domain. `Utils::HmacValidator.validate` will still accept it since it only re-hashes the body, and `Registry.process` will hand the handler a `WebhookMetadata` claiming the payload belongs to the victim shop.

### Impact Explanation
This breaks the shop-identity binding the app relies on for tenant isolation. Since host applications (per this gem's own documented pattern) use `data.shop` to decide which tenant's records to update/create from webhook payloads, an attacker can inject attacker-controlled data (any topic/body they can produce a valid signature for, from their own shop's webhooks) into a victim shop's tenant context — a cross-tenant data integrity/confusion issue reachable by any unprivileged internet user who can install the target app on their own store and capture a webhook.

### Likelihood Explanation
Likelihood is moderate: the attacker needs (1) to install the app themselves (a normal signup, not a privileged account) to receive at least one legitimate webhook body/HMAC pair, and (2) the ability to send arbitrary HTTP requests to the app's public webhook endpoint with custom headers, which is trivial for any internet user. No secret material, TLS interception, or social engineering is required.

### Recommendation
Include the tenant-identifying fields (`shop`, `topic`, `webhook_id`) in the HMAC-signed content, or otherwise cryptographically bind the header-derived shop domain to the signed body (e.g., verify the shop against a shop known to have an active/registered webhook subscription id, and reject webhooks whose `webhook_id` does not resolve to that shop server-side via the Admin API) before handing `WebhookMetadata` to handlers. At minimum, document explicitly that `data.shop` is unauthenticated and must not be trusted for tenant attribution without independent verification.

### Proof of Concept
1. Attacker installs the target Shopify app on their own development/test store (`attacker.myshopify.com`), triggering a legitimate webhook, e.g. `orders/create`, to the app's public callback URL. They capture the raw POST body and the `X-Shopify-Hmac-Sha256` header.
2. Attacker replays the exact same request to the app's webhook endpoint, but changes the `X-Shopify-Shop-Domain` header to `victim.myshopify.com` (a store they do not control), leaving `raw_body` and the HMAC header untouched.
3. `Utils::HmacValidator.validate` recomputes `HMAC(raw_body, api_secret_key)` — identical to what was signed originally — and the comparison in `validate_signature` (`lib/shopify_api/utils/hmac_validator.rb:26-31`) succeeds.
4. `Registry.process` (`lib/shopify_api/webhooks/registry.rb:188-199`) proceeds to call the registered handler with `WebhookMetadata.new(shop: "victim.myshopify.com", ...)`, and any host application following this gem's documented pattern processes the attacker's payload as if it came from the victim shop.

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
