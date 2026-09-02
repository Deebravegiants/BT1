### Title
Webhook `shop-domain` header is not covered by the HMAC signature, allowing tenant spoofing in `ShopifyAPI::Webhooks::Registry.process` - (File: lib/shopify_api/webhooks/request.rb, lib/shopify_api/webhooks/registry.rb)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw request body [1](#0-0) , while the `shop` value handed to the app's webhook handler is read straight from the unauthenticated `x-shopify-shop-domain` / `shopify-shop-domain` header [2](#0-1) . `Registry.process` validates only the HMAC over the body and then dispatches the handler using this unverified header value as the tenant identifier [3](#0-2) .

### Finding Description
The equality the gem is supposed to guarantee is: **the `shop` bytes trusted by the handler == the `shop` bytes cryptographically bound to the verified payload**. Instead, the HMAC only signs `@raw_body` [4](#0-3) [1](#0-0) , and `shop` comes from a header that is never part of the signed content [2](#0-1) [5](#0-4) .

Because the app's `client_secret` (`Context.api_secret_key`) is a single, shared secret used for every shop that installs the app, any shop that has installed the app can independently compute a valid `HMAC-SHA256(secret, body)` for an arbitrary body (Shopify computes and delivers this to that shop for its own legitimate webhook events). `Utils::HmacValidator.validate` only checks that this HMAC matches the body — it never binds the signature to the specific shop the payload claims to be from [6](#0-5) . `Registry.process` then trusts `request.shop` (derived purely from the header) to build `WebhookMetadata` and calls the handler with it [3](#0-2) .

The library's own documentation instructs apps to treat `data.shop` as "The shop domain of the webhook" and use it directly to route/enqueue tenant-specific work [7](#0-6) , so this is the intended, documented use of the field — not a case of the host application ignoring documented guidance.

### Impact Explanation
A merchant who has legitimately installed the app (an "unprivileged" party with respect to other tenants of the same app) can capture a genuine `(body, hmac)` pair generated for their own store, then replay it to the app's webhook endpoint while substituting the `x-shopify-shop-domain` header for a victim shop. The HMAC still validates (it only checks `body`), so `Registry.process` dispatches the (attacker-controlled) body to the handler tagged as belonging to the victim shop. Any host application that uses `data.shop` to select the tenant's session/database record for processing (exactly as shown in the gem's own documentation example) will have attacker data written into or read against the victim tenant. This crosses a tenant/authentication boundary and matches the "cross-tenant access" Critical impact category.

### Likelihood Explanation
Exploitation requires only (a) the attacker to legitimately install the target app on their own store — a normal, unprivileged action available to anyone — and (b) capture one of their own real webhook deliveries (readily observable, since the merchant controls the receiving endpoint or can proxy/log it). No access to the app's `client_secret`, access tokens, or any other tenant's data is required. This is a low-effort, low-skill attack chain.

### Recommendation
- Do not treat the `shop-domain` header as authoritative for tenant identity. Cross-check `request.shop` against the shop associated with the specific `webhook_id`/topic via a server-side lookup (e.g., confirm the shop has an active, stored session/webhook registration matching that `webhook_id`) before dispatching to the handler.
- Alternatively/additionally, extend `VerifiableQuery`/`to_signable_string` for webhooks to incorporate a canonicalized form of the security-relevant headers (`shop-domain`, `topic`, `webhook-id`, `api-version`) into the value being HMAC-verified where feasible, or document explicitly and loudly that `data.shop` is NOT covered by the HMAC and must be independently corroborated by callers against known-installed shops before being used to select a tenant context.

### Proof of Concept
1. Attacker installs the target Shopify app on `attacker-shop.myshopify.com`, obtaining a legitimate installation and receiving real webhook deliveries (e.g., `orders/create`).
2. Attacker captures one legitimate webhook POST, e.g.:
   ```
   POST /callback/orders/create
   x-shopify-topic: orders/create
   x-shopify-hmac-sha256: <valid-hmac-of-body>
   x-shopify-shop-domain: attacker-shop.myshopify.com
   x-shopify-webhook-id: <id>
   Body: {"id": 1, "note": "malicious payload"}
   ```
3. Attacker crafts a new body of their choosing under their own shop, records the resulting valid `x-shopify-hmac-sha256` (they can generate as many body/HMAC pairs as they like since Shopify signs any webhook sent to their own installed shop).
4. Attacker replays the request to the same endpoint, only changing:
   ```
   x-shopify-shop-domain: victim-shop.myshopify.com
   ```
   keeping the same body and HMAC.
5. `Utils::HmacValidator.validate` succeeds because it only checks the body [8](#0-7) ; `Registry.process` calls the handler with `shop: "victim-shop.myshopify.com"` and the attacker-controlled body [3](#0-2) , causing any host logic keyed on `data.shop` to act on the victim tenant using attacker-supplied data.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L10-13)
```ruby
      sig { override.returns(String) }
      def hmac
        Digest.hexencode(Base64.decode64(T.cast(shopify_header("hmac-sha256"), String)))
      end
```

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
