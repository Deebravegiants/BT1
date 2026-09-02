## Finding: Webhook shop/topic identity not bound to HMAC signature [1](#0-0) 

The gem's webhook verification computes the HMAC only over the raw request body — `to_signable_string` returns `@raw_body` — while `shop` and `topic` are taken directly from separate, unauthenticated HTTP headers (`shopify-shop-domain`/`x-shopify-shop-domain`, `shopify-topic`/`x-shopify-topic`).Confirmed: `Registry.process` binds `request.shop` and `request.topic` directly into `WebhookMetadata` as the trusted tenant/topic identity for the handler, but `HmacValidator.validate` only checks the HMAC against `to_signable_string`, which for `Webhooks::Request` returns solely `@raw_body`. [2](#0-1) [3](#0-2) [4](#0-3) 

### Title
Webhook `shop`/`topic` identity fields are not covered by the HMAC signature, allowing cross-tenant webhook spoofing - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw request body, and `HmacValidator.validate` verifies the HMAC solely against that body. The `shop` (`shopify-shop-domain`/`x-shopify-shop-domain`) and `topic` headers, which `Registry.process` treats as authenticated tenant identity and dispatch key, are never included in the signed material.

### Finding Description
The identity binding that should hold is: `hmac_verified(body) == true` should imply `shop` and `topic` used by the handler are the same `shop`/`topic` that the legitimate sender (Shopify) associated with that body. Instead, the code only proves `hmac == HMAC(secret, raw_body)`; it never proves `hmac` was computed over `shop` or `topic`.

`Registry.process` calls `Utils::HmacValidator.validate(request)`, which only invokes `request.to_signable_string` (the raw body) - `lib/shopify_api/webhooks/registry.rb:190` and `lib/shopify_api/utils/hmac_validator.rb:26-31`. After validation succeeds, it immediately trusts `request.shop` and `request.topic`, both parsed straight from attacker-controllable HTTP headers with no cryptographic relationship to the HMAC - `lib/shopify_api/webhooks/registry.rb:198-199`, `lib/shopify_api/webhooks/request.rb:16-23`.

Because Shopify's HMAC over a webhook body is deterministic given `(secret, body)`, any two webhooks that happen to share an identical body (e.g., an empty/near-empty payload, a fixed test payload, or a payload an attacker can also legitimately trigger, such as a `shop/redact` or app-uninstalled webhook body they control from their own store) will validate under the same HMAC signature, and only the header-derived `shop`/`topic` distinguish the events. An unprivileged internet user who can send arbitrary POST requests to the app's public webhook endpoint (this is a normal, internet-reachable endpoint, not requiring credentials) can replay a `(raw_body, hmac)` pair they legitimately obtained from their own shop's webhook, but substitute an arbitrary victim `shop-domain` header, causing the handler to execute business logic as if the event originated from the victim shop.

### Impact Explanation
This breaks the tenant boundary the library is supposed to guarantee to the host application: successful HMAC validation is documented/used as proof that a webhook body belongs to the shop given in the accompanying headers, but the gem itself never binds these together. A host app that (reasonably, per this gem's contract) trusts `WebhookMetadata#shop` after `Registry.process` returns without raising can have data intended for one shop applied to another shop's records — a cross-tenant data-integrity/confusion issue.

### Likelihood Explanation
Exploitability depends on the attacker being able to produce or predict a body whose HMAC they know and that is meaningful when replayed under a different shop header. This is most practical for topics with fixed or attacker-controllable bodies (e.g., compliance webhooks with a payload the attacker's own store can generate), which the attacker fully controls end-to-end since they can operate their own real store as the webhook source, capture the legitimate `(body, hmac)` pair, and resend it with a spoofed `shop`/`topic` header directly to the app's public endpoint.

### Recommendation
Include the `shop` and `topic` (and ideally `webhook_id`) header values in the HMAC-signed material used for verification, or otherwise cryptographically bind them to the body before trusting them in `WebhookMetadata`. At minimum, document and enforce that `shop`/`topic` must be independently corroborated (e.g., cross-checked against a shop the app has an active session/install for) before being used as a tenant key.

### Proof of Concept
1. Attacker installs the target app on their own store `attacker.myshopify.com` and triggers a webhook whose body is fixed/predictable (e.g., an empty-body compliance webhook, or any webhook whose payload the attacker fully controls via their store's data).
2. Attacker captures the legitimate `(raw_body, shopify-hmac-sha256)` pair delivered to the app's public webhook endpoint.
3. Attacker sends a new POST request directly to the same public webhook endpoint with the identical `raw_body`/`hmac` but with `shopify-shop-domain: victim-shop.myshopify.com` (and optionally a different `shopify-topic`).
4. `HmacValidator.validate` in `lib/shopify_api/utils/hmac_validator.rb:13-22` succeeds because it only checks the body against the hmac.
5. `Registry.process` in `lib/shopify_api/webhooks/registry.rb:188-200` dispatches to the handler with `shop: "victim-shop.myshopify.com"`, and the host app processes attacker-controlled data as belonging to the victim tenant.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L10-63)
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

      sig { returns(T::Hash[String, T.untyped]) }
      def parsed_body
        JSON.parse(@raw_body)
      end

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L13-31)
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

        private

        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
```
