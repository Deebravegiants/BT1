Confirmed: this gem's docs explicitly instruct app developers to trust `data.shop` directly (`docs/usage/webhooks.md` line 25-26: `perform_later(topic: data.topic, shop_domain: data.shop, ...)`), and `Registry.process` treats a request as authentic once `Utils::HmacValidator.validate(request)` passes [1](#0-0) , while the HMAC itself is computed only over the raw body [2](#0-1)  and never binds the `shop`, `topic`, `webhook_id`, or `api_version` headers that `Registry.process` hands to the handler as the tenant identifier [3](#0-2) .

### Title
Webhook tenant identity (`shop`) is not bound by the HMAC signature, enabling cross-tenant webhook spoofing - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw request body, excluding the `shop-domain`, `topic`, `webhook-id`, and `api-version` headers from the HMAC-covered data. `Registry.process` validates the HMAC over that body-only string and then unconditionally trusts the unauthenticated `shop` header as the tenant key passed to the app's handler. This breaks the intended identity binding: `shop authenticated by HMAC == shop used as tenant/session key`.

### Finding Description
`Webhooks::Request#to_signable_string` is defined as:
```ruby
def to_signable_string
  @raw_body
end
``` [2](#0-1) 

`shop`, `topic`, `webhook_id`, and `api_version` are all read straight from HTTP headers with no cryptographic binding to the body or to each other [4](#0-3) .

`HmacValidator.validate` computes `HMAC(secret, verifiable_query.to_signable_string)` and compares it to the `hmac` header value using `OpenSSL.secure_compare` [5](#0-4) . Since `to_signable_string` is body-only, this signature proves only "this body byte-sequence was HMAC'd with the app's secret at some point by Shopify for some shop" — it proves nothing about which shop, topic, or webhook the body is currently being claimed to belong to.

`Registry.process` then does:
```ruby
raise Errors::InvalidWebhookError, "Invalid webhook HMAC." unless Utils::HmacValidator.validate(request)
...
handler.handle(data: WebhookMetadata.new(topic: request.topic, shop: request.shop, body: request.parsed_body, ...))
``` [1](#0-0) 

So `request.shop` — read from an unauthenticated header — is handed to the app as the trusted tenant identifier, and the gem's own documentation instructs developers to key persistence/business logic directly off `data.shop` without any further verification [6](#0-5) .

**Equality that should hold but doesn't:** `shop authenticated by the HMAC == shop delivered to the handler as WebhookMetadata#shop`. In reality the HMAC authenticates only the body bytes; the shop field is asserted, not proven.

### Impact Explanation
An unprivileged internet user who can install the same app on any shop they control (any developer/merchant can create a free Shopify dev store and install a public app) can capture one legitimately-signed webhook delivery — a valid `(raw_body, hmac)` pair for their own shop — and then send that exact `(raw_body, hmac)` pair directly to the app's public webhook endpoint with the `shopify-shop-domain` (and optionally `shopify-topic`/`shopify-webhook-id`) headers rewritten to name a *different*, victim tenant shop that also uses the app. Because the HMAC check only re-derives the signature from `@raw_body` and never incorporates the shop header, validation still succeeds, and the forged request is delivered to the handler as if it were an authentic event for the victim shop. This is a cross-tenant data-injection/spoofing primitive: an app that (as instructed by this gem's own docs) uses `data.shop` to select which tenant's records to create/update/queue work for can be made to process attacker-supplied webhook bodies under a victim shop's identity, without ever touching `api_secret_key`, an access token, or TLS interception.

### Likelihood Explanation
Likelihood is meaningful but bounded: the attacker needs at least one legitimately-signed `(body, hmac)` pair, which they can trivially obtain by installing the target app on their own shop and receiving any webhook of a topic the app has registered (no privileged credentials needed — self-installation on a dev/test store is available to any internet user). From there, replaying the pair with a modified shop header is a simple unauthenticated HTTP POST to the app's public callback endpoint. The severity of impact depends entirely on how the consuming app uses `data.shop`, but the gem provides no mitigation or warning, and its documentation actively encourages the unsafe pattern.

### Recommendation
Do not treat `request.shop` as authenticated solely because `HmacValidator.validate` passed. At minimum:
- Document prominently that the HMAC only covers the body and that `shop`/`topic`/`webhook_id` headers are unauthenticated, and that consuming apps must cross-check `request.shop` against a shop for which they have an active, independently-established session/registration before acting on the webhook.
- Consider incorporating the `shop`, `topic`, and `webhook_id` header values into the signable string (or otherwise verifying them against Shopify's known registration for that webhook id via an API call) before handing them to the handler as trusted `WebhookMetadata`.

### Proof of Concept
1. Attacker installs the target app on `attacker-shop.myshopify.com` (any free dev store) and triggers a webhook the app has registered for (e.g. `orders/create`), capturing the raw POST body and the `X-Shopify-Hmac-Sha256` header Shopify sent.
2. Attacker crafts a new HTTP POST to the app's public webhook endpoint, reusing the exact same raw body and HMAC header, but sets:
   - `shopify-shop-domain: victim-shop.myshopify.com`
   - (topic/webhook-id can also be freely set since none are bound by the signature)
3. `Registry.process` calls `HmacValidator.validate(request)`, which recomputes `HMAC(secret, raw_body)` and finds it matches the (unchanged) `hmac` header — validation passes [7](#0-6) .
4. The handler receives `WebhookMetadata.new(topic: ..., shop: "victim-shop.myshopify.com", body: <attacker-controlled JSON>, ...)` [8](#0-7)  and, following the gem's documented pattern, performs tenant-scoped work (e.g. `perform_later(shop_domain: data.shop, webhook: data.body)`) attributing attacker-controlled data to the victim shop.

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L13-22)
```ruby
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

**File:** docs/usage/webhooks.md (L19-30)
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
```
