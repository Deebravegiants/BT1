### Title
Webhook `shop` domain is not covered by the HMAC signature, allowing cross-tenant shop spoofing in `ShopifyAPI::Webhooks::Registry.process` - (File: lib/shopify_api/webhooks/request.rb, lib/shopify_api/webhooks/registry.rb)

### Summary
`ShopifyAPI::Webhooks::Registry.process` validates a webhook solely by checking the HMAC over the raw request body [1](#0-0) . The HMAC computation (`to_signable_string`) only ever returns `@raw_body`; none of the Shopify headers — including `shop-domain` — are part of the signed material [2](#0-1) . The gem then passes `request.shop`, read verbatim from the unauthenticated header, straight into the documented `WebhookMetadata` object delivered to the app's handler [1](#0-0) , and the docs explicitly tell integrators to trust `data.shop` as "The shop domain of the webhook" [3](#0-2) .

### Finding Description
The equality that should hold is: `shop asserted in the X-Shopify-Shop-Domain header == shop whose HMAC secret actually authenticated the delivered bytes`. Because the app's `api_secret_key` is a single, shop-independent secret shared by every merchant that has the app installed [4](#0-3) , and because the HMAC is computed only over `@raw_body` [5](#0-4) , a valid `(body, hmac)` pair obtained from any one installed shop (including a shop the attacker themselves controls, since they can trigger webhooks in their own store) remains cryptographically valid when replayed with an arbitrary `shopify-shop-domain` header value. `Registry.process` never checks that the claimed shop matches anything beyond the topic-handler lookup [1](#0-0) , so `WebhookMetadata.shop` ends up bound to attacker-controlled header data rather than to the HMAC-verified payload.

### Impact Explanation
This breaks the tenant boundary the gem's own documented API promises: the doc tells integrators `data.shop` is a trustworthy field on which to key per-shop actions (e.g., `perform_later(shop_domain: data.shop, ...)`) [6](#0-5) . An attacker who has legitimately installed the app on a shop they control can capture one authentic webhook delivery, then replay it against the app's public webhook endpoint with the `shopify-shop-domain` header rewritten to a victim shop's domain. `Registry.process` will accept it as valid (HMAC passes) and hand the handler a `WebhookMetadata` claiming to be from the victim shop, injecting attacker-controlled body content attributed to another tenant — a cross-tenant data-integrity/spoofing issue that exists entirely inside this gem's own verification logic, not merely a downstream misuse of it.

### Likelihood Explanation
Exploitation only requires: (1) becoming an app user (any merchant can install a public/embedded app), and (2) knowledge of the app's public webhook endpoint, which is standard. No access token, `client_secret`, or privileged credential is needed — only the ability to receive one's own legitimate webhook and replay it with a modified header. This is fully reachable through the gem's public `Registry.process`/`HmacValidator.validate`/`Request#to_signable_string` code path.

### Recommendation
Bind the verified identity to the signed payload instead of trusting the header value independently: cross-check `request.shop` (or the `X-Shopify-Shop-Domain` header) against a shop that is known/expected for the given webhook subscription (e.g., verify it corresponds to a shop that actually has that webhook topic registered / has an active session), or include the shop domain in the signable string used for HMAC verification wherever feasible. At minimum, update `docs/usage/webhooks.md` to explicitly warn that `data.shop` is not covered by the HMAC and must be independently corroborated by the host application before being used for tenant-scoping decisions.

### Proof of Concept
1. App merchant A installs the app on `attacker.myshopify.com` and legitimately receives (or triggers, e.g. via `products/update`) a webhook: body `B`, header `x-shopify-hmac-sha256: H`, header `x-shopify-shop-domain: attacker.myshopify.com`.
2. Attacker POSTs to the app's webhook endpoint the same raw body `B` and the same `x-shopify-hmac-sha256: H`, but sets `x-shopify-shop-domain: victim.myshopify.com`.
3. `ShopifyAPI::Webhooks::Request.new` parses headers normally (no header validation beyond presence) [7](#0-6) .
4. `Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes HMAC over `to_signable_string` (== `B`) and compares against `H` — it matches, since neither depends on the shop header [8](#0-7) [9](#0-8) .
5. The handler receives `WebhookMetadata.new(..., shop: "victim.myshopify.com", body: parsed(B), ...)` [10](#0-9)  and, following the documented usage pattern, processes/persists data attributed to `victim.myshopify.com` even though it never sent this webhook.

### Citations

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

**File:** lib/shopify_api/webhooks/request.rb (L20-43)
```ruby
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

      sig { returns(T::Hash[String, T.untyped]) }
      def parsed_body
        JSON.parse(@raw_body)
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

**File:** docs/usage/webhooks.md (L12-30)
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
