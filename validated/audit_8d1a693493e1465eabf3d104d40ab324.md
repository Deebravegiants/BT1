This confirms the vulnerability: `ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`, so the HMAC computed by `HmacValidator.validate` covers exclusively the raw request body. The `shop-domain` and `topic` values consumed by `Registry.process` and forwarded to the app's `WebhookHandler#handle` via `WebhookMetadata` are read straight from HTTP headers, outside the signed bytes. [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3) 

### Title
Webhook `shop-domain` header is not covered by the HMAC, allowing cross-tenant webhook spoofing — (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` binds the `shop` (and `topic`) it hands to the application's webhook handler to the `X-Shopify-Shop-Domain` HTTP header, but the HMAC signature that the gem verifies covers only the raw request body (`to_signable_string` returns `@raw_body`). Any request whose body/HMAC pair is valid for *some* shop can be replayed with the `shop-domain` header rewritten to a different, victim shop, and `Registry.process` will still accept it and dispatch attacker-supplied data to the handler tagged as coming from the victim shop.

### Finding Description
`HmacValidator.validate` computes `OpenSSL::HMAC.hexdigest(sha256, api_secret_key, verifiable_query.to_signable_string)` and compares it (via `OpenSSL.secure_compare`) to the signature taken from the `X-Shopify-Hmac-Sha256` header. [5](#0-4) 

For webhooks, `to_signable_string` is defined to return only `@raw_body`: [6](#0-5) 

Meanwhile `shop`, `topic`, `api_version`, and `webhook_id` are all read directly from HTTP headers that are never mixed into the signed bytes: [7](#0-6) 

`Registry.process` only checks `Utils::HmacValidator.validate(request)` (i.e., body integrity) before trusting `request.topic` and forwarding `request.shop` straight into `WebhookMetadata`, which is what the app-supplied `WebhookHandler#handle` consumes to decide which tenant the payload belongs to: [3](#0-2) [4](#0-3) 

This breaks the intended identity binding: `shop-domain header == the shop whose credentials/secret produced the HMAC`. In reality the equality that actually holds is only `HMAC == f(raw_body, api_secret_key)`; the header is unauthenticated and can be swapped freely by anyone who can produce (or already possesses) one valid `(body, HMAC)` pair for any shop on the same app, since all shops of a given app share the same `api_secret_key`.

### Impact Explanation
Because every shop installed on the same app is verified with the identical `Context.api_secret_key`, an attacker who controls their own myshopify store (an "unprivileged internet user" from Shopify's perspective, but a legitimate merchant of the app) can:
1. Trigger any webhook topic on their own store to receive a genuine `(raw_body, HMAC)` pair signed with the app's shared secret.
2. Replay that exact body and HMAC to the app's public webhook endpoint, but with the `X-Shopify-Shop-Domain` (and optionally `X-Shopify-Topic`) header changed to a victim shop's domain.
3. `HmacValidator.validate` still succeeds (it only checks the body), so `Registry.process` dispatches the (attacker-authored) payload to the handler labeled with the victim's `shop`.

Depending on how the host application persists webhook data (order records, inventory updates, GDPR/`customers/redact` compliance actions, etc.), this enables cross-tenant data injection/corruption — an attacker forging events attributed to a shop they do not own. This matches the Critical category "cross-tenant access" since the tenant identity binding used by the app is derived from unauthenticated bytes.

### Likelihood Explanation
Any app built on this gem that installs on multiple merchants shares one `api_secret_key` across shops (this is standard Shopify OAuth app architecture — the `client_secret`/`api_secret_key` is per-app, not per-shop). An attacker only needs to be a legitimate/trial installer of the target app on their own store to obtain a valid `(body, HMAC)` pair, then craft an HTTP request with a modified `shop-domain` header — no access token, no `client_secret`, and no privileged access to Shopify's infrastructure is required.

### Recommendation
Include the shop domain (and topic) inside the signed material, or otherwise cryptographically bind them to the HMAC before trusting them. Concretely, `ShopifyAPI::Webhooks::Request#to_signable_string` should incorporate `shop`, `topic` (and ideally `webhook_id`) alongside `@raw_body`, or `Registry.process`/`HmacValidator` should independently verify that the shop asserted in the header matches a shop-specific secret/session rather than trusting the unauthenticated header outright.

### Proof of Concept
```ruby
# Attacker installs the target app on their own store "attacker.myshopify.com"
# and triggers, e.g., an "orders/create" webhook, capturing:
raw_body = '{"id":1,"note":"hello"}'
valid_hmac_b64 = Base64.encode64(
  OpenSSL::HMAC.digest(OpenSSL::Digest.new("sha256"), APP_SECRET, raw_body)
) # this is what Shopify legitimately sent to the app for attacker's own shop

# Attacker replays it to the app's public webhook endpoint, spoofing the header:
headers = {
  "x-shopify-topic" => "orders/create",
  "x-shopify-hmac-sha256" => valid_hmac_b64,       # unchanged, still valid
  "x-shopify-shop-domain" => "victim-shop.myshopify.com", # attacker-controlled, unauthenticated
}

request = ShopifyAPI::Webhooks::Request.new(raw_body: raw_body, headers: headers)
ShopifyAPI::Utils::HmacValidator.validate(request) # => true, because only raw_body is checked
ShopifyAPI::Webhooks::Registry.process(request)
# handler.handle is invoked with WebhookMetadata(shop: "victim-shop.myshopify.com", body: attacker JSON)
```
The handler processes attacker-controlled data as if it originated from `victim-shop.myshopify.com`, because the gem never binds `shop-domain` to the HMAC.

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
