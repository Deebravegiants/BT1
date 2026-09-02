### Title
Webhook `shop` and `topic` identity fields are not covered by the HMAC signature, enabling cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` implements `Utils::VerifiableQuery` and is validated via `Utils::HmacValidator.validate`, but the HMAC signature only covers the raw request body — never the `shop`, `topic`, `webhook_id`, or `api_version` values that are read directly from HTTP headers. `Registry.process` trusts these header-derived fields to build the `WebhookMetadata` passed to the app's handler, breaking the binding between "bytes verified by HMAC" and "identity fields acted upon."

### Finding Description
`Request#to_signable_string` returns only the raw body:

```ruby
sig { override.returns(String) }
def to_signable_string
  @raw_body
end
``` [1](#0-0) 

Meanwhile `shop`, `topic`, `api_version`, and `webhook_id` are all pulled straight from attacker-controllable headers, with no cryptographic binding to those values:

```ruby
def topic
  T.cast(shopify_header("topic"), String)
end

def shop
  T.cast(shopify_header("shop-domain"), String)
end
``` [2](#0-1) 

`HmacValidator.validate` computes the signature only over `verifiable_query.to_signable_string` (i.e., the body) and compares it to the `hmac` value, never incorporating the headers:

```ruby
def validate(verifiable_query)
  return false unless verifiable_query.hmac
  result = validate_signature(verifiable_query, Context.api_secret_key)
  ...
end
``` [3](#0-2) 

`Registry.process` performs this same HMAC check and then unconditionally trusts `request.shop` and `request.topic` to construct the metadata dispatched to the host application's handler:

```ruby
def process(request)
  raise Errors::InvalidWebhookError, "Invalid webhook HMAC." unless Utils::HmacValidator.validate(request)
  handler = @registry[request.topic]&.handler
  ...
  handler.handle(data: WebhookMetadata.new(topic: request.topic, shop: request.shop,
    body: request.parsed_body, api_version: request.api_version, webhook_id: request.webhook_id))
end
``` [4](#0-3) 

**Binding that should hold but doesn't:** `HMAC-verified(bytes)` should equal `bytes the app treats as authoritative for identity (shop, topic)`. Here, `HMAC-verified(bytes) = raw_body`, while `identity used by handler = headers(shop, topic)`, which are two disjoint byte ranges. An attacker who can obtain one legitimately-signed `(raw_body, hmac)` pair for the app's secret (e.g., by installing the app on their own store and capturing a webhook Shopify delivers to them) can resend that exact body/HMAC pair to the app's webhook endpoint while substituting an arbitrary `shopify-shop-domain` and `shopify-topic` header. `HmacValidator.validate` will still return `true` because it never inspects the headers, and `Registry.process` will hand the handler a `WebhookMetadata` claiming to be for a different shop/topic than the one that actually produced the signed body.

### Impact Explanation
This crosses a tenant boundary: an unprivileged party who legitimately installs the app on their own shop can forge webhook deliveries that the host application will process as belonging to a different shop or topic, entirely by replaying an HMAC that was validly issued for their own tenant's payload. Any host application logic that uses `WebhookMetadata#shop`/`#topic` to select which tenant's data to update (a documented, expected usage pattern of this library) can be manipulated into acting on the wrong shop — i.e., cross-tenant access/manipulation, which meets the Critical impact bar in the rules.

### Likelihood Explanation
Likelihood is limited by the need for the attacker to obtain at least one legitimately signed `(body, hmac)` pair, which any merchant who installs the app can trivially get by having their own store deliver a webhook to the app (or simply resending their own webhook with tampered headers). No secrets, tokens, or privileged access are required beyond ordinary use of the app as an installing merchant.

### Recommendation
Bind the shop/topic identity into the HMAC-verified surface, or otherwise cryptographically tie the header-derived identity fields to the value verified by HMAC. Concretely:
- Include `shop`, `topic`, `api_version`, and `webhook_id` in `to_signable_string` (matching what Shopify actually signs, if it signs headers) rather than the body alone, or
- Require host applications to look up shop context from a source outside of headers (e.g., an out-of-band authenticated session) before trusting `WebhookMetadata#shop`, and clearly document that `shop`/`topic` from `Webhooks::Request` are unauthenticated header values not covered by HMAC verification.

### Proof of Concept
1. Attacker installs the target app on their own store `attacker-shop.myshopify.com`, granting them a legitimate webhook subscription.
2. Shopify delivers a legitimate webhook to the app's endpoint with body `B` and header `x-shopify-hmac-sha256: H`, where `H = HMAC-SHA256(api_secret_key, B)`. `x-shopify-shop-domain: attacker-shop.myshopify.com` and `x-shopify-topic: orders/create`.
3. Attacker replays the exact same `B` and `H` to the app's webhook endpoint, but rewrites headers to `x-shopify-shop-domain: victim-shop.myshopify.com` and/or a different `x-shopify-topic`.
4. `ShopifyAPI::Utils::HmacValidator.validate(request)` in `lib/shopify_api/utils/hmac_validator.rb` returns `true` because it only recomputes HMAC over `@raw_body` (`B`), which is unchanged.
5. `ShopifyAPI::Webhooks::Registry.process` in `lib/shopify_api/webhooks/registry.rb` dispatches the handler with `WebhookMetadata.new(topic: "orders/create", shop: "victim-shop.myshopify.com", body: parsed(B), ...)`, causing the host app to process data under the wrong tenant's identity despite a "valid" HMAC check.

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L12-22)
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
