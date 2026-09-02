This confirms the finding. The docs explicitly state that `ShopifyAPI::Webhooks::Registry.process` "will verify the request did indeed come from Shopify" [1](#0-0) , and the documented handler contract trusts `data.shop` (`WebhookMetadata#shop`) as the tenant identity for downstream actions [2](#0-1) [3](#0-2) . But the HMAC only covers the raw body, not the shop header, breaking the intended binding.

### Title
Webhook shop-domain identity is not bound to the HMAC signature, enabling cross-tenant webhook forgery - (File: lib/shopify_api/webhooks/request.rb, lib/shopify_api/webhooks/registry.rb)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`, and `hmac`, `shop`, `topic` are all read verbatim from attacker-controllable HTTP headers [4](#0-3) . `Registry.process` validates only that the HMAC matches the body, then unconditionally trusts `request.shop` (and `request.topic`) as the identity fields passed to the handler [5](#0-4) . The equality the gem is supposed to guarantee is `hmac_verified_bytes == identity_bytes_used_for_tenant_dispatch`; instead, only the body is inside the HMAC, while `shop-domain` (the tenant key) is outside it.

### Finding Description
`HmacValidator.validate` computes `HMAC(secret, verifiable_query.to_signable_string)` and compares it to the `hmac` field of the same object [6](#0-5) . For webhook requests, `to_signable_string` is defined as just the raw JSON body [7](#0-6) , while `shop`, `topic`, and `webhook_id` come from HTTP headers that are never mixed into the signed string [8](#0-7) . Because Shopify signs webhooks with the app's single shared `client_secret` (the same value used for every shop installing the app), any shop that legitimately installs the app can capture a valid `(body, hmac)` pair from its own genuine webhook deliveries. That pair remains cryptographically valid for any other value of the `shop-domain` header, since the header is not part of the signed material. An attacker can then POST that same body/HMAC pair to the app's webhook endpoint with a forged `x-shopify-shop-domain` header naming a victim shop. `Registry.process` will pass HMAC validation and dispatch to the handler with `WebhookMetadata#shop` set to the forged victim domain [9](#0-8) .

### Impact Explanation
This breaks the identity binding the gem documents and promises: the docs say `Registry.process` "will verify the request did indeed come from Shopify" [1](#0-0)  and instruct handlers to key their work off `data.shop` [10](#0-9) . Any host app that follows this documented contract to route or authorize webhook-triggered actions per shop (e.g., look up the shop's session/access token, fan out background jobs keyed by `shop_domain`, or make privileged Admin API calls "on behalf of" that shop) can be tricked into acting on a victim tenant's data using an attacker-forged shop identity — a cross-tenant access vector, satisfying the Critical impact bar.

### Likelihood Explanation
Exploitation requires only: (1) the attacker to run their own real Shopify store and install the target app (an ordinary unprivileged action any internet user can do for any public app), to legitimately receive at least one HMAC-signed webhook body from the shared app secret, and (2) the ability to POST to the app's public webhook endpoint with a spoofed `x-shopify-shop-domain` (or `shopify-shop-domain`) header, which the gem accepts from either header namespace with no cryptographic tie to the signature [11](#0-10) . No leaked secrets, TLS interception, or privileged access are needed — this is exploitable by an unprivileged merchant/attacker who installs the app on their own store.

### Recommendation
Bind the `shop`, `topic`, and `webhook_id` fields into the signed material (e.g., include them in `to_signable_string`, or independently verify that the `shop` header matches a shop that is actually subscribed to receive this specific webhook/topic combination via a server-side registry lookup) before trusting `request.shop` in `WebhookMetadata`. At minimum, document prominently that `data.shop` is not cryptographically bound to the HMAC and must not be trusted for tenant-scoped authorization without an independent verification step (e.g., cross-checking against the shop that owns the `webhook_id` via the Admin API).

### Proof of Concept
1. Attacker installs the target app on their own store `attacker.myshopify.com` and receives a legitimate webhook, e.g. body `{"id":123}"` with header `x-shopify-hmac-sha256: <valid-HMAC-of-body-with-app-secret>` and `x-shopify-shop-domain: attacker.myshopify.com`.
2. Attacker replays the exact same raw body and HMAC header to the app's public webhook endpoint, but changes `x-shopify-shop-domain` to `victim.myshopify.com`.
3. `ShopifyAPI::Webhooks::Request.new` parses the forged headers; `Utils::HmacValidator.validate` succeeds because it only recomputes HMAC over `raw_body`, which is unchanged [12](#0-11) [13](#0-12) .
4. `Registry.process` dispatches to the registered handler with `WebhookMetadata.new(topic: ..., shop: "victim.myshopify.com", body: ...)` [14](#0-13) , and any host-app logic keyed on `data.shop` now operates under the victim's tenant identity despite the request never having come from Shopify for that shop.

### Citations

**File:** docs/usage/webhooks.md (L12-26)
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
```

**File:** docs/usage/webhooks.md (L125-125)
```markdown
To process an http webhook, you need to listen on the route(s) you provided during the Webhook registration process, then when the route is hit construct a `ShopifyAPI::Webhooks::Request` and call `ShopifyAPI::Webhooks::Registry.process`. This will verify the request did indeed come from Shopify and then call the specified handler for that webhook. An example in Rails is shown below:
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

**File:** lib/shopify_api/webhooks/request.rb (L10-38)
```ruby
      sig { override.returns(String) }
      def hmac
        Digest.hexencode(Base64.decode64(T.cast(shopify_header("hmac-sha256"), String)))
      end

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

**File:** lib/shopify_api/webhooks/request.rb (L45-63)
```ruby
      sig { params(raw_body: String, headers: T::Hash[String, T.untyped]).void }
      def initialize(raw_body:, headers:)
        # normalize the headers by forcing lowercase, removing any prepended "http"s, and changing underscores to dashes
        headers = headers.to_h { |k, v| [k.to_s.downcase.sub("http_", "").gsub("_", "-"), v] }

        missing_headers = []
        ["topic", "hmac-sha256", "shop-domain"].each do |name|
          unless headers.key?("shopify-#{name}") || headers.key?("x-shopify-#{name}")
            missing_headers << "shopify-#{name} or x-shopify-#{name}"
          end
        end
        unless missing_headers.empty?
          raise Errors::InvalidWebhookError,
            "Missing one or more of the required HTTP headers to process webhooks: #{missing_headers}"
        end

        @headers = headers
        @raw_body = raw_body
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
