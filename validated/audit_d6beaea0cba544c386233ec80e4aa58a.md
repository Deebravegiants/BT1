This confirms the vulnerability. The gem's documentation itself states "This will verify the request did indeed come from Shopify" for `ShopifyAPI::Webhooks::Registry.process`, but the shop identity is not actually part of that verification.

### Title
Webhook shop-domain header is trusted for tenant identification without being covered by the HMAC signature - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Registry.process` claims to "verify the request did indeed come from Shopify" [1](#0-0) , but the HMAC computed by `Utils::HmacValidator` only signs the raw request body, never the `shop`, `topic`, `webhook_id`, or `api_version` values that are read straight from HTTP headers. [2](#0-1)  These unauthenticated header values, in particular `shop`, are handed directly to the app's webhook handler as the tenant identifier. [3](#0-2) 

### Finding Description
`Request#to_signable_string` returns only `@raw_body`. [4](#0-3)  `HmacValidator.validate` computes the HMAC exclusively over that signable string and compares it to the `hmac` header via `OpenSSL.secure_compare`. [5](#0-4)  Meanwhile `shop`, `topic`, `webhook_id`, and `api_version` are pulled straight out of the `shopify-*`/`x-shopify-*` headers with no cryptographic binding to the body or the HMAC. [6](#0-5) 

`Registry.process` only checks `Utils::HmacValidator.validate(request)` before dispatching `request.shop` (and the other header-derived fields) to the app's handler as trusted, verified data: [7](#0-6) 

```ruby
def process(request)
  raise Errors::InvalidWebhookError, "Invalid webhook HMAC." unless Utils::HmacValidator.validate(request)
  handler = @registry[request.topic]&.handler
  ...
  handler.handle(data: WebhookMetadata.new(topic: request.topic, shop: request.shop,
    body: request.parsed_body, api_version: request.api_version, webhook_id: request.webhook_id))
end
```

This breaks the identity binding: `shop that was HMAC-authenticated` should equal `shop that the handler acts on`, but the gem only authenticates the body bytes, not the `shop-domain` header. The gem's own documentation encourages host apps to trust `data.shop` directly as the tenant key (e.g. `perform_later(topic: data.topic, shop_domain: data.shop, ...)`). [8](#0-7) 

An unprivileged attacker who controls (or has previously observed) any single legitimately-signed webhook delivery for their own shop — trivially obtainable since any merchant can install the app and trigger webhooks on their own store — has a `(raw_body, hmac)` pair that is valid under `HmacValidator.validate` regardless of what the `x-shopify-shop-domain` header says, because that header plays no role in the signature. Replaying that same body/HMAC pair to the app's webhook endpoint with an altered `x-shopify-shop-domain` header (naming a victim shop) passes HMAC validation and is delivered to the handler as if it genuinely originated from the victim shop.

### Impact Explanation
This enables cross-tenant impersonation via webhook: an attacker-controlled request, using only a signature they can legitimately obtain for their own tenant, is misattributed to an arbitrary target shop. Depending on how the host application's `WebhookHandler` acts on `data.shop` (e.g., queuing tenant-scoped background jobs, invalidating tokens, updating tenant records, or triggering `shop/redact` / `app/uninstalled`-style flows), this can lead to cross-tenant data corruption, spoofed uninstall/redact events for a shop the attacker doesn't own, or poisoning of tenant-keyed queues/caches — a cross-tenant boundary violation.

### Likelihood Explanation
High likelihood: the attacker only needs a webhook delivery for their own store (attainable by any merchant who installs the app or configures any webhook subscription pointed to a URL they control to capture the body+HMAC), and no secret material (`api_secret_key`, access token) is required to exploit the impersonation itself — only to obtain the initial legitimate signature for their own tenant, which any merchant naturally has.

### Recommendation
Bind the tenant identity to the signed payload before trusting it: either require the webhook body to be parsed and cross-checked against a `shop` field already present in Shopify's webhook payloads where guaranteed, or otherwise document/require that host applications MUST independently verify `request.shop` against a shop they expect (e.g., a shop that has a live installation/session), rather than the gem implicitly asserting the webhook "did indeed come from Shopify" for that shop. At minimum, update `docs/usage/webhooks.md` to remove the implication that `Registry.process` authenticates the shop identity, and clarify that `data.shop` is unauthenticated header data.

### Proof of Concept
1. Attacker installs the app on their own shop `attacker.myshopify.com` and configures/receives one legitimate webhook delivery, capturing `raw_body` and the `x-shopify-hmac-sha256` header value (both perfectly valid, since HMAC is computed only over `raw_body` with the real `api_secret_key`, as in `HmacValidator.validate_signature`). [9](#0-8) 
2. Attacker POSTs the same `raw_body` and `hmac` to the app's registered webhook endpoint, but sets `x-shopify-shop-domain: victim-shop.myshopify.com`.
3. `Request.new` parses headers/body without validating `shop` against anything. [10](#0-9) 
4. `Registry.process` calls `Utils::HmacValidator.validate(request)`, which passes because it only checks `raw_body` + `hmac`. [11](#0-10) 
5. `handler.handle` is invoked with `WebhookMetadata.new(shop: "victim-shop.myshopify.com", ...)`, and the host app processes it as an authenticated event for the victim shop. [12](#0-11)

### Citations

**File:** docs/usage/webhooks.md (L24-27)
```markdown
    def handle(data:)
      puts "Received webhook! topic: #{data.topic} shop: #{data.shop} body: #{data.body} webhook_id: #{data.webhook_id} api_version: #{data.api_version}"
      perform_later(topic: data.topic, shop_domain: data.shop, webhook: data.body)
    end
```

**File:** docs/usage/webhooks.md (L125-125)
```markdown
To process an http webhook, you need to listen on the route(s) you provided during the Webhook registration process, then when the route is hit construct a `ShopifyAPI::Webhooks::Request` and call `ShopifyAPI::Webhooks::Registry.process`. This will verify the request did indeed come from Shopify and then call the specified handler for that webhook. An example in Rails is shown below:
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
