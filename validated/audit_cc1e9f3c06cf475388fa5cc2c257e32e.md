### Title
Webhook `shop`/`topic` identity fields are not covered by the HMAC signature, allowing tenant spoofing on an otherwise-valid webhook - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw HTTP body, while `shop`, `topic`, `webhook_id`, and `api_version` are read directly from unauthenticated HTTP headers. `Utils::HmacValidator.validate` only checks the HMAC over that signable string (the body). The tenant identity (`shop`) that `Registry.process` hands to the app's webhook handler is therefore never bound to the cryptographic signature.

### Finding Description
`Webhooks::Request#to_signable_string` is defined as: [1](#0-0) 
which returns only `@raw_body`. The `shop`, `topic`, `webhook_id`, and `api_version` accessors instead read straight from caller-supplied headers with no cross-check against the signed payload: [2](#0-1) 

`HmacValidator.validate` computes the HMAC purely over `to_signable_string` (i.e., the body) and compares it to the `hmac` header: [3](#0-2) 

`Registry.process` trusts the HMAC check and then forwards `request.shop`/`request.topic` — values that were never part of the signed bytes — directly to the app's handler as the tenant identity: [4](#0-3) 

The gem's own documentation instructs apps to use `data.shop` from the handler callback as the authoritative shop/tenant identifier for the webhook payload: [5](#0-4) 

This is the exact bug class from the report generalized to an identity binding: the check (`HMAC valid?`) answers a different question than the one being trusted (`is this body+shop-domain pairing authentic?`). The equality that should hold but doesn't is:
`shop bound by HMAC == shop acted upon by the handler`
Here, "shop acted upon" (`request.shop`, taken from the `X-Shopify-Shop-Domain` header) is not an input to `to_signable_string`, so it can be swapped freely by anyone who can reach the webhook endpoint with any body+HMAC pair that is valid for that body — the header value itself carries no authenticity guarantee.

### Impact Explanation
Any entity that can obtain one genuinely-signed `(raw_body, hmac)` pair for the app's `client_secret` (e.g., an attacker who installs the app on their own store and receives a legitimate webhook) can replay that same body/HMAC pair to the app's public webhook endpoint while substituting the `shop-domain` header for a victim shop. `HmacValidator.validate` will still return `true` (the body is unmodified and the HMAC matches), and `Registry.process` will invoke the handler with `WebhookMetadata#shop` set to the attacker-chosen victim domain. If the host application uses `data.shop` — as this gem's own documentation instructs — to select which tenant's records to update (the intended and only documented usage pattern), an attacker can inject fabricated data attributed to a different merchant's tenant, i.e., cross-tenant data confusion/injection using only a signature that was never meant to authenticate that shop.

### Likelihood Explanation
Requires only unauthenticated network access to the app's public webhook callback URL plus possession of one legitimately-signed webhook body for the same `client_secret` (trivially obtainable by installing the target app on an attacker-controlled development store, which typical Shopify app installation flows allow to any developer). No access token, API key, or the app's `client_secret` value itself is needed — only a previously observed valid `(body, hmac)` pair. This is entirely reachable through this gem's documented `Registry.process` / `Webhooks::Request` API with no reliance on the host app deviating from documented usage.

### Recommendation
Bind the identity headers into the signed payload verification, e.g., include `shop`, `topic`, and `webhook_id` in `to_signable_string` (or otherwise cryptographically bind them, such as by having the host verify `shop` against its own webhook registration state before trusting the payload), so that the HMAC check fails if any of these fields are altered independently of the body.

### Proof of Concept
1. Attacker installs the target app on their own shop `attacker.myshopify.com`, and Shopify delivers a legitimate webhook with `X-Shopify-Hmac-Sha256: H`, body `B`, and `X-Shopify-Shop-Domain: attacker.myshopify.com`.
2. Attacker replays a POST to the same app webhook endpoint with the identical body `B` and header `X-Shopify-Hmac-Sha256: H`, but sets `X-Shopify-Shop-Domain: victim.myshopify.com`.
3. `ShopifyAPI::Webhooks::Registry.process` computes `Utils::HmacValidator.validate(request)`, which only hashes `@raw_body` (`B`) — unchanged — so validation succeeds: [1](#0-0) 
4. `Registry.process` invokes the app's handler with `WebhookMetadata.new(... shop: request.shop ...)`, where `request.shop` now returns `"victim.myshopify.com"`: [6](#0-5) 
5. The host application, following the documented handler contract, processes attacker-controlled body content under the victim's tenant.

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

**File:** docs/usage/webhooks.md (L12-30)
```markdown
`data` will have the following keys
- `topic`, `String` - The topic of the webhook
- `shop`, `String` - The shop domain of the webhook
- `body`, `T::Hash[String, T.untyped]`- The body of the webhook
- `webhook_id`, `String` - The id of the webhook event to [avoid duplicates](https://shopify.dev/docs/apps/webhooks/best-practices#ignore-duplicates)
- `api_version`, `String` - The api version of the webhook

```ruby
module WebhookHandler
  extend ShopifyAPI::Webhooks::WebhookHandler

  class << self
    def handle(data:)
      puts "Received webhook! topic: #{data.topic} shop: #{data.shop} body: #{data.body} webhook_id: #{data.webhook_id} api_version: #{data.api_version}"
      perform_later(topic: data.topic, shop_domain: data.shop, webhook: data.body)
    end
  end
end
```
```
