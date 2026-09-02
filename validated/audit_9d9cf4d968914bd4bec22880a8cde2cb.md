This confirms the vulnerability path. The `Webhooks::Request#hmac` is verified only against `@raw_body` (`to_signable_string`), while `shop`, `topic`, `webhook_id`, and `api_version` come from HTTP headers that are never part of the signed payload.This confirms the full path: `Registry.process` validates the HMAC via `HmacValidator.validate(request)`, which only checks `request.to_signable_string` (the raw body) against the HMAC header, then passes `request.shop` — a value read directly from the unauthenticated `x-shopify-shop-domain` header — into `WebhookMetadata` and the app's handler, unbound from the signature.### Title
Webhook `shop` (and `topic`/`webhook_id`) identity fields are not covered by the HMAC signature, allowing cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` verifies webhook authenticity by HMAC-signing only the raw request body, while the `shop`, `topic`, `webhook_id`, and `api_version` fields consumed by the host application are parsed from unauthenticated HTTP headers that are never part of the signed payload. This breaks the identity binding `HMAC(body) == verified` vs. `shop header == trusted tenant identity`, letting a holder of any single valid `(raw_body, hmac)` pair relabel the `shop` field to any other tenant and have the app process it as if it came from that victim shop.

### Finding Description
`HmacValidator.validate` computes the signature over `verifiable_query.to_signable_string` and compares it to the `hmac` field via `OpenSSL.secure_compare`: [1](#0-0) 

For webhook requests, `to_signable_string` returns only the raw body (`@raw_body`), and the HMAC itself is read from the `hmac-sha256` header: [2](#0-1) 

Crucially, `shop`, `topic`, `webhook_id`, and `api_version` are all read directly from HTTP headers (`shop-domain`, `topic`, `webhook-id`, `api-version`) that are **not** included in `to_signable_string` and therefore are never covered by the HMAC: [3](#0-2) 

`Registry.process` validates only the HMAC over the body, then unconditionally trusts `request.shop`/`request.topic`/`request.webhook_id` from headers and forwards them into the app's own `WebhookHandler`: [4](#0-3) 

`WebhookMetadata` is the struct the host application's business logic operates on, using `shop` as the tenant identifier for the webhook body: [5](#0-4) 

Root cause: this gem's own `Request`/`Registry`/`HmacValidator` code binds authenticity to the body bytes only, not to the tenant-identifying header (`shop-domain`). Since Shopify's webhook `api_secret_key` is a single app-wide secret shared across *all* installed shops (not shop-specific), any shop that legitimately receives a webhook from Shopify obtains a `(raw_body, valid hmac)` pair signed with that same app-wide secret. That pair remains HMAC-valid regardless of which `shop-domain` header accompanies it, because the header is outside the signed content.

### Impact Explanation
An attacker who controls (or has installed) the app on their own shop receives real webhooks with valid HMACs signed with the app's shared `client_secret`. By replaying the same `raw_body` + `hmac-sha256` value to the app's webhook endpoint while substituting a different `x-shopify-shop-domain` header (naming a victim tenant), `HmacValidator.validate` still returns `true` (body+HMAC match), and `Registry.process` hands the forged `shop` straight to the handler as `WebhookMetadata#shop`. Any host application that uses this `shop` value to select/update per-tenant data (the gem's own documented pattern, since `WebhookMetadata#shop` is the only tenant identifier provided) will act on the victim tenant's records using attacker-supplied body content — i.e., cross-tenant data injection/corruption within the multi-tenant boundary this gem is meant to enforce. This satisfies the High-severity "cross-tenant access" criterion since the identity binding between the verified bytes and the trusted tenant field is broken by this gem's own code, not by host misuse.

### Likelihood Explanation
Likelihood is high for any multi-tenant app built on this gem: the prerequisite (having one valid, own-shop webhook payload+HMAC pair) is trivially satisfiable by any user who installs the app on their own shop — no privileged credentials, leaked secrets, or social engineering required, satisfying the "unprivileged internet user" constraint. The replay itself is a simple HTTP POST to the app's public webhook endpoint with a modified header.

### Recommendation
Bind the `shop` (and ideally `topic`/`webhook_id`) to the HMAC-verified content, e.g. by including the `shop-domain` header value in `to_signable_string`, or by having the host verify that the `shop` extracted from the header matches an independently-trusted source (e.g., the shop stored against the registered webhook subscription id) before trusting `WebhookMetadata#shop`. At minimum, document that `WebhookMetadata#shop` is unauthenticated and must not be relied upon as a tenant boundary without additional verification.

### Proof of Concept
1. Attacker installs the target app on their own shop `attacker.myshopify.com` and receives a legitimate webhook: `raw_body = B`, header `x-shopify-hmac-sha256 = H` (valid signature of `B` using the app's shared `api_secret_key`), header `x-shopify-shop-domain = attacker.myshopify.com`.
2. Attacker POSTs the same `B` and `H` to the app's webhook endpoint but sets `x-shopify-shop-domain: victim.myshopify.com`.
3. `ShopifyAPI::Webhooks::Request.new(raw_body: B, headers: {...shop-domain: "victim.myshopify.com", hmac-sha256: H...})` is constructed; [6](#0-5) 
4. `Registry.process(request)` calls `Utils::HmacValidator.validate(request)`, which succeeds because it only checks `B` against `H`: [7](#0-6) 
5. The handler receives `WebhookMetadata.new(..., shop: "victim.myshopify.com", body: parsed(B), ...)`, and the host app processes attacker-controlled body content as belonging to `victim.myshopify.com`.

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
