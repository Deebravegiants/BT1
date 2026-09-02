### Title
Webhook `shop` identity is not bound to the HMAC signature, enabling cross-tenant webhook spoofing - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Registry.process` verifies a webhook's authenticity by HMAC-validating only the raw request body, while the `shop` value that the gem hands to application handlers (and that the docs tell developers to trust for tenant identification) is taken from an HTTP header that is never covered by that HMAC. This breaks the identity binding `shop attributed to payload == shop that Shopify actually signed the payload for`, allowing cross-tenant webhook spoofing.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw body bytes: [1](#0-0) 

`shop` is read from the `shopify-shop-domain` / `x-shopify-shop-domain` header, completely independent of the signed data: [2](#0-1) 

`Registry.process` validates the HMAC of the body only, then forwards `request.shop` unchanged into `WebhookMetadata` given to the app's handler: [3](#0-2) 

`HmacValidator.validate` / `validate_signature` compute the digest solely over `verifiable_query.to_signable_string` (the body), never mixing in the shop header: [4](#0-3) 

Because the `shop-domain` header is excluded from the signed payload, any request carrying a *previously valid* `(body, hmac)` pair will pass verification regardless of which shop domain header accompanies it. The documented handler contract explicitly instructs developers to treat `data.shop` as the authoritative tenant identifier: [5](#0-4) [6](#0-5) 

This is precisely the reported bug class translated to this gem: a field ("shop") that business logic acts on is not covered by the HMAC that is meant to authenticate the whole message.

### Impact Explanation
An unprivileged internet user who can install the app on their own shop (a normal, permission-less action) receives genuine Shopify webhooks for that shop, each with a valid `(body, hmac)` pair signed with the app's real `client_secret`. Because the `X-Shopify-Shop-Domain` header is not part of the signed material, the attacker can replay that same `(body, hmac)` pair to the app's webhook endpoint while substituting the `shop-domain` header with an arbitrary victim shop's domain. `Registry.process` will accept it as authentic (`HmacValidator.validate` succeeds) and hand the handler a `WebhookMetadata` claiming the (attacker-controlled) body belongs to the victim shop. Any host application following the gem's documented pattern (`shop_domain: data.shop`) will attribute attacker-controlled webhook data to a shop it does not belong to — a cross-tenant data-injection/spoofing primitive, satisfying the "cross-tenant access" Critical-impact bucket.

### Likelihood Explanation
Likelihood is Medium-High: no secrets, tokens, or privileged access are required — only the ability to install the app on an attacker-owned shop (an ordinary, unauthenticated OAuth flow) and the ability to relay HTTP requests with modified headers, which is trivial for any client sending directly to the app's public webhook endpoint.

### Recommendation
Bind the shop (and ideally topic/webhook-id) into the signed material, or otherwise cryptographically tie the header-derived shop to the verified body, e.g.:
- Include `shop`, `topic`, and `webhook_id` in `to_signable_string`, or
- Require the consuming application to independently confirm that `data.shop` corresponds to a shop for which an active, previously-established session/installation exists before trusting it, and document this requirement prominently in `docs/usage/webhooks.md`.
- At minimum, update `Utils::HmacValidator` to include the shop header in the payload actually hashed against `Context.api_secret_key`.

### Proof of Concept
1. Attacker installs the target app on `attacker-shop.myshopify.com` and registers a webhook (e.g. `orders/create`).
2. Shopify sends a legitimate webhook request to the app's endpoint with headers `X-Shopify-Shop-Domain: attacker-shop.myshopify.com`, `X-Shopify-Hmac-Sha256: <valid hmac over body>`, and a JSON body the attacker fully controls (crafted by placing arbitrary data on their own orders).
3. Attacker captures this exact `(raw_body, hmac)` pair.
4. Attacker resends the identical `raw_body` and `hmac` to the app's webhook endpoint, but replaces the header with `X-Shopify-Shop-Domain: victim-shop.myshopify.com`.
5. `ShopifyAPI::Webhooks::Request.new` parses the forged header [7](#0-6) , and `Registry.process` calls `Utils::HmacValidator.validate(request)`, which succeeds because it only checks `@raw_body` against the hmac [3](#0-2) .
6. The application's handler receives `WebhookMetadata` with `shop == "victim-shop.myshopify.com"` and attacker-controlled `body`, processing it as if it were legitimate data for the victim tenant.

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
```

**File:** docs/usage/webhooks.md (L12-16)
```markdown
`data` will have the following keys
- `topic`, `String` - The topic of the webhook
- `shop`, `String` - The shop domain of the webhook
- `body`, `T::Hash[String, T.untyped]`- The body of the webhook
- `webhook_id`, `String` - The id of the webhook event to [avoid duplicates](https://shopify.dev/docs/apps/webhooks/best-practices#ignore-duplicates)
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
