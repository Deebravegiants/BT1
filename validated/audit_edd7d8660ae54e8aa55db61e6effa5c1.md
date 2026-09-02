This confirms the finding: `WebhookMetadata#shop` is documented and used by handlers as the trusted shop identity [1](#0-0) , but `ShopifyAPI::Webhooks::Registry.process` derives `shop` purely from the `shop-domain` header while only the HMAC validates the raw body [2](#0-1) , and `Request#to_signable_string` returns only `@raw_body`, excluding all headers from the signed content [3](#0-2) . `HmacValidator.validate` computes the signature strictly over `to_signable_string` using the app's shared `api_secret_key` [4](#0-3) .

### Title
Webhook `shop-domain` header is trusted for tenant attribution but is not covered by the HMAC signature - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` signs only the raw JSON body, while the `shop`, `topic`, `webhook-id`, and `api-version` values are read from unauthenticated HTTP headers. `Registry.process` validates the HMAC over the body alone, then passes the header-derived `shop` straight into `WebhookMetadata`, which host applications are documented to use as the authoritative tenant identifier for the event.

### Finding Description
`Registry.process` performs exactly one authentication check — the HMAC over the raw body — before trusting `request.shop`: [2](#0-1) 

The signable string used for that HMAC is defined as the raw body only: [3](#0-2) 

`shop`, `topic`, `webhook_id`, and `api_version` are all pulled from headers that are never part of the signed material: [5](#0-4) 

Because `api_secret_key` is a single app-wide secret shared across every shop that installs the app (not shop-specific), any shop that legitimately receives one real webhook from Shopify obtains a `(body, hmac)` pair whose signature will validate successfully under `HmacValidator.validate` regardless of which `shop-domain` header value accompanies it: [4](#0-3) 

The binding that should hold is: **shop asserted in `WebhookMetadata.shop` == shop that the HMAC-verified bytes actually originated from**. Because the header is excluded from the signable string, this equality is never enforced — the gem lets an attacker satisfy "HMAC valid" while supplying an arbitrary `shop` value. The documentation confirms host apps are expected to key their persisted data directly off `data.shop`: [6](#0-5) 

### Impact Explanation
A merchant who installs the vulnerable app (an unprivileged action requiring no special access) will receive genuine webhook deliveries signed with the app's shared secret. By replaying the exact same request body with the `X-Shopify-Shop-Domain` header changed to a victim shop's domain, the attacker produces a request that passes `Registry.process`'s only integrity check and is delivered to the handler tagged as belonging to the victim shop. Any host application following the documented pattern (persisting/acting on data keyed by `data.shop`) will write attacker-controlled webhook content into the victim tenant's records — a cross-tenant data-integrity breach, which maps to the Critical "cross-tenant access" category.

### Likelihood Explanation
Likelihood is high for any app that installs on more than one shop: the attacker needs only (1) to install the target app themselves to receive one legitimately-signed webhook, and (2) resend it with a modified header — both are unprivileged, unauthenticated-relative-to-other-tenants actions requiring no access to `api_secret_key`, TLS interception, or social engineering.

### Recommendation
Include the shop domain (and ideally topic/webhook id) in the HMAC-signed material, or independently verify that the `shop-domain` header matches a shop known to have an active, registered webhook subscription/session before constructing `WebhookMetadata`, rather than trusting the header value on the strength of a body-only HMAC.

### Proof of Concept
1. App `X` is installed on attacker's shop `attacker.myshopify.com` and on victim's shop `victim.myshopify.com`, both using the same `api_secret_key`.
2. Attacker's shop receives a legitimate webhook, e.g. `orders/create`, with body `B` and header `X-Shopify-Hmac-Sha256: H`, where `H = HMAC-SHA256(api_secret_key, B)`.
3. Attacker resends `POST /callback/orders/create` to the app's webhook endpoint with body `B`, header `X-Shopify-Hmac-Sha256: H` (unchanged, still valid since only `B` is signed), but `X-Shopify-Shop-Domain: victim.myshopify.com`.
4. `Registry.process` calls `Utils::HmacValidator.validate(request)`, which succeeds because it only checks `HMAC(api_secret_key, B) == H`, per [7](#0-6) .
5. `WebhookMetadata.shop` is set to `"victim.myshopify.com"` from the (unauthenticated) header, per [8](#0-7) , and the host app's handler processes attacker-controlled order data as if it belonged to the victim shop.

### Citations

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

**File:** lib/shopify_api/webhooks/request.rb (L15-38)
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

**File:** docs/usage/webhooks.md (L10-30)
```markdown
If you want to register for an http webhook you need to implement a webhook handler which the `shopify_api` gem can use to determine how to process your webhook. You can make multiple implementations (one per topic) or you can make one implementation capable of handling all the topics you want to subscribe to. To do this simply make a module or class that includes or extends `ShopifyAPI::Webhooks::WebhookHandler` and implement the `handle` method which accepts the following named parameters: data: `WebhookMetadata`. An example implementation is shown below:

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
