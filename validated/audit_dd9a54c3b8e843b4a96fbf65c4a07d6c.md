This confirms the finding: the docs at `docs/usage/webhooks.md` explicitly instruct developers to trust `data.shop` as the tenant identifier (`shop_domain: data.shop`), and `WebhookMetadata#shop` is defined as `const :shop, String` in `lib/shopify_api/webhooks/webhook_handler.rb`, sourced directly from the unauthenticated `shop-domain`/`x-shopify-shop-domain` HTTP header.

### Title
Webhook `shop` (tenant) identifier is not covered by HMAC verification, enabling cross-tenant impersonation - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` validates a webhook solely by checking `Utils::HmacValidator.validate(request)`, which in turn calls `request.to_signable_string`. For `ShopifyAPI::Webhooks::Request`, `to_signable_string` returns only `@raw_body`, while `shop`, `topic`, `webhook_id`, and `api_version` are all read straight out of HTTP headers that are never included in the HMAC computation. The gem then hands this unauthenticated `shop` value directly to the app's handler as the tenant identifier.

### Finding Description
`ShopifyAPI::Utils::HmacValidator.validate` computes the expected signature over `verifiable_query.to_signable_string` and compares it to the `hmac` value with `OpenSSL.secure_compare`: [1](#0-0) 

For webhook requests, `to_signable_string` is defined as just the raw request body: [2](#0-1) 

Meanwhile `shop`, `topic`, `webhook_id`, and `api_version` are parsed from HTTP headers with no cryptographic binding to the HMAC at all: [3](#0-2) 

`Registry.process` performs the HMAC check and then constructs `WebhookMetadata` using `request.shop` taken from that unauthenticated header, passing it straight to the developer's handler as the trusted tenant identity: [4](#0-3) [5](#0-4) 

The identity binding that should hold is: `shop attributed to the event == shop that produced the signed bytes`. Because the HMAC is computed with the app's single, shared `client_secret` across *all* shops that install the app (not a per-shop secret), and the signature covers only the body, any two requests with identical (or attacker-reproducible) bodies from *different* shops installed on the same app can be freely relabeled: an attacker who operates their own shop installation of the app can capture one legitimate Shopify-signed webhook (valid HMAC over a body they control/can trigger, e.g. by editing a product on their own store) and replay it to the app's webhook endpoint with the `shop-domain`/`x-shopify-shop-domain` header rewritten to a victim shop's domain. `HmacValidator.validate` still returns `true` because the signature only ever depended on the body and the shared secret, never on the `shop` header, so `Registry.process` accepts the forged request and calls the handler with `WebhookMetadata#shop` set to the victim's domain. [6](#0-5) 

The official usage docs confirm the host app is expected to key persistence/business logic directly off `data.shop` without any additional cross-check against the HMAC: [7](#0-6) 

### Impact Explanation
This breaks the tenant boundary the gem is responsible for enforcing at the webhook ingestion point: it allows one merchant (an "unprivileged internet user" from the app's perspective, since they only control their own shop's installation) to inject events that the host application will process as if they originated from a different, victim merchant. Depending on how the host app persists webhook data keyed by `data.shop` (order sync, inventory updates, uninstall/GDPR events, etc.), this can lead to cross-tenant data corruption or spoofed state changes attributed to a shop the attacker does not control.

### Likelihood Explanation
Exploitation requires only that the attacker install the app on their own (attacker-controlled) shop — a normal, unprivileged action requiring no leaked secrets, no TLS interception, and no access to `api_secret_key`. From there, they can trigger events on their own store to obtain validly HMAC-signed bodies and replay them against the webhook endpoint with a forged `shop-domain` header, since nothing in `Utils::HmacValidator` or `Webhooks::Request` binds the signature to the shop.

### Recommendation
Include the shop domain (and ideally topic/webhook id) inside the HMAC-covered signable string for webhooks, or otherwise cryptographically bind the `shop` header to the signed payload before trusting it as the tenant identifier in `WebhookMetadata`.

### Proof of Concept
1. Attacker installs the app on their own shop `attacker.myshopify.com`, obtaining valid webhook deliveries signed with the app's shared `client_secret`.
2. Attacker triggers an event (e.g., `products/update`) on their own shop and captures the raw body `B` and its valid `x-shopify-hmac-sha256` header `H` — `H` is valid because `HmacValidator` computes it purely from `B` and the shared secret: [8](#0-7)  and [9](#0-8) .
3. Attacker POSTs body `B` with header `H` unchanged, but sets `x-shopify-shop-domain: victim.myshopify.com`.
4. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which passes since only `B` and the shared secret matter: [6](#0-5) .
5. The handler is invoked with `WebhookMetadata#shop == "victim.myshopify.com"`, and the host app processes/persists the forged event under the victim's tenant.

### Citations

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

**File:** docs/usage/webhooks.md (L12-29)
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
