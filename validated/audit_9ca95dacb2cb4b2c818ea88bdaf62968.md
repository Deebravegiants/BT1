This confirms the finding: `ShopifyAPI::Webhooks::Request#shop` (from the `shopify-shop-domain`/`x-shopify-shop-domain` header) is documented and used as the tenant identifier passed to the handler via `WebhookMetadata`, but it is not covered by the HMAC signature, which is computed only over `@raw_body`.### Title
Cross-tenant webhook spoofing via unauthenticated `shop-domain` header in `ShopifyAPI::Webhooks::Request` - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an inbound webhook solely by validating an HMAC computed over the raw request body, while the `shop` value used downstream as the tenant identifier is read from an HTTP header that is never included in that HMAC computation. This breaks the intended binding `shop authenticated == shop the payload is attributed to`, letting a webhook that is validly signed for one shop be replayed with a forged `shop-domain` header claiming to be a different shop.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`Registry.process` verifies the webhook exclusively via `Utils::HmacValidator.validate(request)`, which in turn calls `to_signable_string` (i.e., only the raw body bytes) against the app's `Context.api_secret_key`: [2](#0-1) [3](#0-2) 

However, `Request#shop` is read directly from the `shopify-shop-domain`/`x-shopify-shop-domain` HTTP header, a field that is completely outside the HMAC-signed payload: [4](#0-3) [5](#0-4) 

This `shop` value is then passed straight into `WebhookMetadata` and handed to the app's registered handler as the shop of record for the event: [2](#0-1) 

Because the app's `api_secret_key` (`client_secret`) is shared across every shop that has installed the app — not shop-specific — any merchant who has legitimately installed the app can trigger a webhook on their own store and obtain a genuinely valid `(raw_body, hmac)` pair signed with the app's shared secret. Since the `shop-domain` header is not part of the signed material, that merchant can replay the same body/HMAC pair against the app's webhook endpoint while substituting a different shop's domain in the `X-Shopify-Shop-Domain` header. `HmacValidator.validate` still returns true because it only checks the body, so `Registry.process` calls the handler with `WebhookMetadata#shop` set to the forged victim domain, even though the payload actually originated from (and was signed for) the attacker's own shop.

The documented usage pattern in `docs/usage/webhooks.md` explicitly instructs apps to key business logic off `data.shop`: [6](#0-5) 

so this is not a case of the host app "ignoring documented API" — it is following the gem's documented contract, and the gem itself fails to bind the trusted `shop` value to the HMAC-authenticated bytes.

### Impact Explanation
This is a cross-tenant identity confusion: data or events legitimately signed for shop A can be attributed to shop B purely by header manipulation, with no possession of shop B's credentials required. Depending on what the app's webhook handler does with `data.shop` (e.g., writing order/customer data into shop B's records, invalidating shop B's cache, or acting on shop B's session), this can result in cross-tenant data corruption or unauthorized actions taken against a victim merchant's tenant — satisfying the "cross-tenant access" criterion.

### Likelihood Explanation
Likelihood is limited by the fact that the attacker must be a merchant who has genuinely installed the app (to receive a validly-signed webhook from Shopify in the first place), and must be able to send a raw HTTP request with a modified `shop-domain` header directly to the app's webhook endpoint (bypassing/spoofing whatever transport occurred). This is plausible for any installed merchant, since no `api_secret_key` or access token theft is required — only observation of one's own legitimately delivered webhook traffic and header injection.

### Recommendation
Bind the shop identity to the authenticated payload instead of trusting an unsigned header: include the shop domain (and ideally topic) as part of the string that is HMAC-verified, or independently verify that the `shop-domain` header value matches a shop the app has an active, previously-established session/webhook registration for before dispatching to the handler in `Registry.process`.

### Proof of Concept
1. App has `client_secret` `S`, and shop `attacker.myshopify.com` legitimately installs the app.
2. Shopify sends a real webhook to the app for `attacker.myshopify.com`: body `B`, header `X-Shopify-Hmac-Sha256: HMAC(S, B)`, header `X-Shopify-Shop-Domain: attacker.myshopify.com`.
3. Attacker captures this `(B, HMAC(S,B))` pair (e.g., by pointing their own webhook subscription's callback URL through a proxy they control, which is allowed since they own the shop's webhook configuration for their own tenant).
4. Attacker resends `POST /callback/<topic>` to the app with body `B`, the same `X-Shopify-Hmac-Sha256` header, but `X-Shopify-Shop-Domain: victim.myshopify.com`.
5. `ShopifyAPI::Webhooks::Request.new(raw_body: B, headers: {...})` → `Registry.process` → `Utils::HmacValidator.validate` succeeds (body unchanged) → handler is invoked with `WebhookMetadata.new(shop: "victim.myshopify.com", body: parsed_body, ...)`, causing the app to process attacker-controlled event data as if it belonged to `victim.myshopify.com`.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L20-23)
```ruby
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

**File:** lib/shopify_api/webhooks/request.rb (L45-70)
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

      private

      sig { params(name: String).returns(T.untyped) }
      def shopify_header(name)
        @headers["shopify-#{name}"] || @headers["x-shopify-#{name}"]
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
