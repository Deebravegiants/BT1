### Title
Webhook `shop-domain` (and `topic`/`webhook-id`/`api-version`) Headers Are Not Covered by HMAC, Allowing Cross-Tenant Webhook Spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC-signable content solely from the raw request body [1](#0-0) , while the `shop`, `topic`, `webhook_id`, and `api_version` values that `Registry.process` hands to the app's handler are read directly, unauthenticated, from HTTP headers [2](#0-1) . `Utils::HmacValidator.validate` only checks the body against the signature [3](#0-2) , so the `shop-domain` header that identifies the tenant is never bound to the signed payload.

### Finding Description
`ShopifyAPI::Webhooks::Registry.process` validates a webhook purely via `Utils::HmacValidator.validate(request)` and then immediately trusts `request.shop` as the tenant identity passed to the app's handler:

```ruby
def process(request)
  raise Errors::InvalidWebhookError, "Invalid webhook HMAC." unless Utils::HmacValidator.validate(request)
  handler = @registry[request.topic]&.handler
  ...
  handler.handle(data: WebhookMetadata.new(topic: request.topic, shop: request.shop,
    body: request.parsed_body, api_version: request.api_version, webhook_id: request.webhook_id))
end
``` [4](#0-3) 

`HmacValidator.validate` computes the signature only over `to_signable_string`, and for `Request` that is defined as just the raw body:
```ruby
def to_signable_string
  @raw_body
end
``` [1](#0-0) 

Meanwhile `shop`, `topic`, `webhook_id`, and `api_version` are read straight from headers with no cryptographic binding to the signed body:
```ruby
def shop
  T.cast(shopify_header("shop-domain"), String)
end
``` [5](#0-4) 

The equality that should hold is: `shop bound by HMAC == shop delivered to the handler`. In this implementation, `shop bound by HMAC` is undefined (the HMAC binds nothing about tenant identity) while `shop delivered to handler` is attacker-controllable via the `X-Shopify-Shop-Domain` header. Because a single app's webhooks for *all* installed shops are signed with the same `api_secret_key` (the app's client secret, not a per-shop secret), any merchant who has legitimately installed the app can trigger a real webhook to their own shop, capture the resulting valid `(body, hmac)` pair, and then replay that exact body/HMAC to the app's webhook endpoint while substituting a victim shop's domain in the `shop-domain` header (and/or a different `topic`/`webhook-id`). `HmacValidator.validate` will still succeed because the signature check never inspects those headers, and the forged request will be delivered to the handler tagged with the victim's shop identity.

### Impact Explanation
This breaks the tenant-isolation guarantee webhook consumers rely on: an app that uses `WebhookMetadata#shop` to decide which merchant's records to create/update/delete can be made to apply attacker-supplied webhook bodies against another tenant's data. This is a cross-tenant access/data-integrity violation reachable by any user who has (or can obtain) a legitimate, low-privilege installation of the vulnerable app on their own shop — no `api_secret_key`, access token, or other privileged credential is required from the attacker to mount the replay; they only need a webhook that Shopify itself signs for their own store.

### Likelihood Explanation
Likelihood is High for any multi-tenant app built on this gem's webhook handling without additional out-of-band shop verification: the attack only requires installing the app (self-service in the Shopify App Store flow) and triggering an event that causes Shopify to send a webhook to the app (e.g., placing an order, updating a product) — actions fully within a normal merchant's own control. Capturing and replaying an HTTP request with modified headers is trivial.

### Recommendation
Include the identity-relevant headers (`shop-domain`, `topic`, `webhook-id`, `api-version`) in the HMAC-signable content, or otherwise cryptographically bind them to the payload before trusting them (e.g., require that the shop is recorded against the webhook subscription id via a Shopify API lookup rather than trusted from the header). At minimum, `to_signable_string` in `lib/shopify_api/webhooks/request.rb` should incorporate these header values so that tampering with them invalidates the HMAC check in `lib/shopify_api/utils/hmac_validator.rb`.

### Proof of Concept
1. Attacker installs the vulnerable app on `attacker-shop.myshopify.com` (a normal, unprivileged installation).
2. Attacker triggers a real event (e.g., updates a product) causing Shopify to POST a genuine webhook to the app's webhook endpoint, with headers `X-Shopify-Shop-Domain: attacker-shop.myshopify.com`, `X-Shopify-Topic: products/update`, `X-Shopify-Hmac-Sha256: <valid HMAC of raw body>` and a JSON body the attacker fully controls (their own product data).
3. Attacker replays this exact captured request to the same endpoint, but rewrites `X-Shopify-Shop-Domain` to `victim-shop.myshopify.com` (leaving `raw_body` and `X-Shopify-Hmac-Sha256` unchanged).
4. `Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes the HMAC over `@raw_body` only and matches the unchanged signature — validation succeeds [6](#0-5) .
5. The handler receives `WebhookMetadata` with `shop: "victim-shop.myshopify.com"` and `body` fully controlled by the attacker, causing the app to act on the victim's data using attacker-forged content.

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
