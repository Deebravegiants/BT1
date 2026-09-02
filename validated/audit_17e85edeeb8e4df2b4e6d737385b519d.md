### Title
Webhook shop/topic identity is not covered by the HMAC signature, allowing cross-tenant event spoofing via replay - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an incoming webhook solely by validating the HMAC over the raw request body, but the `shop`, `topic`, `webhook_id`, and `api_version` values that are handed to the app's handler and used as the tenant/routing identity are taken from unauthenticated HTTP headers that are never part of the signed bytes.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`ShopifyAPI::Utils::HmacValidator.validate` computes the HMAC exclusively over `to_signable_string` (i.e., the raw body) and compares it with the received `hmac` header: [2](#0-1) 

`Registry.process` uses this validation as its sole authentication check, then immediately trusts `request.shop`, `request.topic`, `request.webhook_id`, and `request.api_version` — all parsed straight from headers, none of them covered by the signature — to build the `WebhookMetadata` passed to the app's handler: [3](#0-2) 

```ruby
sig { params(request: Request).void }
def process(request)
  raise Errors::InvalidWebhookError, "Invalid webhook HMAC." unless Utils::HmacValidator.validate(request)
  handler = @registry[request.topic]&.handler
  ...
  handler.handle(data: WebhookMetadata.new(topic: request.topic, shop: request.shop,
    body: request.parsed_body, api_version: request.api_version, webhook_id: request.webhook_id))
end
```

`request.shop`/`request.topic` are simple header lookups with no relation to the signed payload: [4](#0-3) 

Critically, the HMAC secret used for webhook verification is the app's single `api_secret_key` (`Context.api_secret_key`), shared across **all** shops that install the app — it is not a per-shop secret: [5](#0-4) 

**The broken binding, expressed as an equality that fails to hold:**
`bytes verified (raw_body under HMAC) == bytes/fields acted upon (shop header, topic header, webhook_id header)` — the code assumes these are the same trust domain, but only the first is cryptographically bound to Shopify's authorization.

**Before/after the attacker's request sequence:**
- Before: Attacker installs the app on their own shop (a normal, unprivileged action any merchant can perform) and receives genuine webhook deliveries for that shop, each with a valid `(raw_body, hmac)` pair signed with the app's shared secret.
- Attack: Attacker replays that exact `raw_body`/`hmac` pair to the app's webhook endpoint, but substitutes the `X-Shopify-Shop-Domain` (and/or `X-Shopify-Topic`) header with an arbitrary/victim shop domain or topic of their choosing.
- After: `Utils::HmacValidator.validate` still succeeds (it only checked the untouched body bytes against the shared secret), and `Registry.process` dispatches the handler with `WebhookMetadata#shop` set to the attacker-chosen value, even though that shop never sent or authorized this event.

This is a direct analog to the reported bug class: a value ("shop"/"topic") that is *acted upon* downstream (as the tenant key) is not part of the *validated* data (the HMAC-covered bytes), mirroring "bytes verified versus bytes parsed" and "shop authenticated versus shop stored as identity key" divergence.

### Impact Explanation
The webhook `shop` field is the only tenant identifier the host application receives from this library's webhook processing path; the accompanying documentation explicitly instructs apps to key their downstream processing (job queues, DB updates, etc.) off `data.shop`: [6](#0-5) 

Because `shop`/`topic` are unauthenticated, any merchant who has installed the app (an unprivileged, self-service action) can forge webhook events that the app attributes to a different, victim shop, or reroute a captured payload to a handler for a topic it never legitimately triggered. Depending on the app's handler logic (e.g., "fulfil order for shop X", "update inventory for shop X", "uninstall app for shop X"), this enables cross-tenant data corruption or cross-tenant actions performed under a spoofed shop identity — meeting the "cross-tenant access" criterion for Critical impact.

### Likelihood Explanation
Likelihood is high for any app author following the gem's documented pattern (`Registry.process`) exactly as shown in the docs, since the vulnerability requires no privileged access — only the attacker's own (legitimately installed) app instance to harvest a valid `(body, hmac)` pair, which is then replayed with modified headers to the same public webhook endpoint.

### Recommendation
Include the tenant/routing metadata (`shop`, `topic`, `webhook_id`, `api_version`) in the HMAC-covered signable string, or otherwise cryptographically bind them (e.g., verify `shop`/`topic` headers against values embedded in the signed body, or require Shopify's webhook UUID + timestamp headers to be part of the signature check) inside `Webhooks::Request#to_signable_string` and `Registry.process`, so that any header used for authorization/routing decisions is provably part of the same trust boundary as the HMAC signature.

### Proof of Concept
1. Install the target app on attacker-owned shop `attacker.myshopify.com`; trigger any subscribed webhook topic to receive a legitimate `POST` with body `B` and header `X-Shopify-Hmac-Sha256: H` (valid because `H = HMAC(api_secret_key, B)`, and `api_secret_key` is shared across all installs of the app).
2. Replay the request to the app's webhook endpoint, keeping body `B` and header `X-Shopify-Hmac-Sha256: H` unchanged, but replacing `X-Shopify-Shop-Domain: attacker.myshopify.com` with `X-Shopify-Shop-Domain: victim.myshopify.com` (and/or altering `X-Shopify-Topic`).
3. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes `HMAC(api_secret_key, B)` — still equal to `H` — so validation passes.
4. `Registry.process` dispatches `handler.handle(data: WebhookMetadata.new(shop: "victim.myshopify.com", topic: ..., body: B, ...))`, causing the app to process attacker-controlled data under the victim shop's identity.

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

**File:** docs/usage/webhooks.md (L19-29)
```markdown
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
