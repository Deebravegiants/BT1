This confirms the vulnerability: `ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body` [1](#0-0) , while `shop`, `topic`, `webhook_id`, and `api_version` are read directly from unauthenticated HTTP headers [2](#0-1) . `Registry.process` validates only this body-derived HMAC and then forwards the header-derived `shop` straight into `WebhookMetadata`, which the host app's handler uses to attribute the webhook to a tenant [3](#0-2) .

### Title
Webhook `shop` (and `topic`/`webhook_id`) identity is trusted from unauthenticated headers while only the request body is HMAC-verified, allowing cross-tenant webhook spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` implements `VerifiableQuery` but binds only the raw body to the HMAC signature via `to_signable_string` [1](#0-0) . The `shop`, `topic`, `api_version`, and `webhook_id` values are read from HTTP headers that are never included in the signed material [2](#0-1) . `Utils::HmacValidator.validate` only checks `verifiable_query.to_signable_string` against the HMAC [4](#0-3) , so a signature that is valid for a given body says nothing about which shop, topic, or webhook it belongs to. `Registry.process` treats a valid signature as proof the whole request "did indeed come from Shopify" (per the gem's own documentation) [3](#0-2)  and hands the header-derived `shop` field directly to the app's `WebhookHandler#handle` as part of `WebhookMetadata` [5](#0-4) .

### Finding Description
The identity binding that should hold is: `shop cryptographically bound in HMAC == shop delivered to the handler`. In this gem that equality does not hold — the HMAC only binds `raw_body`, and `shop`/`topic`/`webhook_id` are parsed from headers outside the signed scope [6](#0-5) . Since every shop that installs the same app shares the same `api_secret_key` used to compute webhook HMACs (per Shopify's app-level secret model), any actor who can obtain one genuine, validly-signed webhook body+HMAC pair for their *own* shop can replay that exact body/HMAC pair to the app's webhook endpoint while substituting the `shopify-shop-domain` (and/or `shopify-topic`, `shopify-webhook-id`) header for a different shop that also uses the same app. `Registry.process` will still call `Utils::HmacValidator.validate(request)` successfully because it only re-computes the HMAC over `raw_body`, which is unchanged [7](#0-6) . The handler then receives `WebhookMetadata` claiming the (attacker-chosen) victim shop, with body content actually authored under the attacker's own shop [8](#0-7) .

### Impact Explanation
This breaks the tenant boundary the gem is documented to enforce ("verify the request did indeed come from Shopify") [9](#0-8) . An app relying on `WebhookMetadata#shop` to select the tenant's database record/session (a common, expected usage pattern since the field exists specifically for that purpose) can be made to apply attacker-supplied data (order data, GDPR redact payload content, product data, etc.) to another merchant's tenant, i.e., cross-tenant data injection/corruption without ever needing the target's or the app's `client_secret`, access token, or any privileged access — only participation as an app-installing merchant is required.

### Likelihood Explanation
Any unprivileged actor who can install the app on their own store (a normal, unprivileged flow for public apps) can capture a legitimate webhook delivery to their own endpoint (or via a public testing tool) and replay it with a forged `shopify-shop-domain` header to the same shared endpoint. No secret material needs to be discovered because the header is simply outside the signed scope — this is a low-effort, repeatable attack once one genuine webhook is observed.

### Recommendation
Bind `shop` (and ideally `topic`/`webhook_id`) into the signed material, or otherwise require the gem's `process` API to also verify that the header-derived `shop` matches an authenticated/allow-listed value before constructing `WebhookMetadata`, and update the documentation so it accurately states that only the body is authenticated rather than "the request."

### Proof of Concept
1. Attacker installs the app on `attacker-shop.myshopify.com` and receives a legitimate webhook: body `B`, valid header `shopify-hmac-sha256: H` (computed over `B` with the shared `api_secret_key`), and `shopify-shop-domain: attacker-shop.myshopify.com`.
2. Attacker sends a new HTTP request to the same webhook endpoint with the same body `B` and same `H`, but changes the header to `shopify-shop-domain: victim-shop.myshopify.com`.
3. `ShopifyAPI::Webhooks::Request.new` parses `shop` from the (forged) header [10](#0-9) .
4. `Registry.process` calls `Utils::HmacValidator.validate(request)`, which passes because it only checks `B` against `H` [7](#0-6) .
5. The handler receives `WebhookMetadata(shop: "victim-shop.myshopify.com", body: <attacker's data>, ...)` and processes it as if it were `victim-shop`'s authentic webhook [8](#0-7) .

### Citations

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

**File:** docs/usage/webhooks.md (L125-125)
```markdown
To process an http webhook, you need to listen on the route(s) you provided during the Webhook registration process, then when the route is hit construct a `ShopifyAPI::Webhooks::Request` and call `ShopifyAPI::Webhooks::Registry.process`. This will verify the request did indeed come from Shopify and then call the specified handler for that webhook. An example in Rails is shown below:
```
