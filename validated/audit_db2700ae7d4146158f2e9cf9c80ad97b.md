### Title
Webhook `shop`, `topic`, and `webhook_id` are trusted from HTTP headers but are not covered by the HMAC signature, enabling cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC signature only over the raw request body, while the shop domain, topic, and webhook id are read directly from unauthenticated HTTP headers and passed on to the host app's handler as trusted identity data. Since the `client_secret`/`api_secret_key` used to sign webhooks is shared across every merchant that installs a given app (it is not per-shop), any merchant who receives a legitimate webhook for their own shop can replay the exact same body+HMAC while substituting a different `shop-domain` header, and the signature check still passes.

### Finding Description
`Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`Request#shop`, `#topic`, and `#webhook_id` are parsed straight from the (attacker-controllable, in a replay scenario) headers, with no cryptographic binding to the body that was signed: [2](#0-1) 

`Registry.process` validates only the HMAC of the body via `Utils::HmacValidator.validate`, then immediately builds `WebhookMetadata` using the unauthenticated `request.shop`, `request.topic`, and `request.webhook_id` fields and dispatches it to the app's handler: [3](#0-2) 

`HmacValidator.validate`/`validate_signature` only ever recompute the signature from `verifiable_query.to_signable_string` (i.e., the raw body) and the app's `api_secret_key`; the shop-domain header plays no role in the signature at all: [4](#0-3) 

Because the same `api_secret_key` signs webhooks for *every* shop that installs the app, an authenticated-but-unprivileged merchant (attacker) who installs the app on their own store can:
1. Receive a legitimate webhook for their own shop, capturing the raw body and its valid `x-shopify-hmac-sha256` value.
2. Replay that exact body and HMAC to the app's webhook endpoint, but with the `x-shopify-shop-domain` header changed to a victim shop's domain.
3. `HmacValidator.validate` still succeeds, because the header is not part of the signed content.
4. The host app's handler receives `WebhookMetadata` claiming the payload originated from the victim shop, breaking the binding "shop the HMAC secret actually authenticates" == "shop the handler is told the data belongs to".

This is exactly the "field acted on but not covered by the HMAC" identity-binding gap: the shop identity that the handler trusts is not the shop identity that the signature actually authenticates.

### Impact Explanation
This is a cross-tenant data-confusion/injection vector: an app that stores or acts on webhook payloads keyed by `WebhookMetadata#shop` (as the library's documented usage pattern encourages, since `request.shop` is exposed specifically for that purpose) can be made to process another merchant's data under the wrong tenant, or vice versa — writing an attacker-controlled payload into a victim shop's records. This matches the Critical "cross-tenant access" impact bucket.

### Likelihood Explanation
The attacker only needs to be a normal merchant with the app installed (or intercept/observe one legitimate webhook delivery to their own shop) — no access token, `client_secret`, or privileged account is required. Discovering a victim shop's `myshopify.com` domain is trivial (it's the shop's own public storefront domain). The replay itself is a simple HTTP POST with modified headers.

### Recommendation
Bind the shop/topic/webhook identity into the signed material, or otherwise verify it out-of-band (e.g., cross-check `request.shop` against the caller's known/registered shop for the session making the request, rather than trusting the header on its own). At minimum, the library should not expose `Request#shop` as an implicitly-trusted identity value derived solely from a header that the HMAC does not cover; documentation and `WebhookMetadata` construction should make clear this field is unauthenticated and must be revalidated by the host app against a known shop/session record before being used for any data routing decision.

### Proof of Concept
```ruby
# Attacker (merchant on shop-a.myshopify.com) captures a real webhook delivery:
raw_body = '{"id":1,"note":"legit order"}'
hmac = OpenSSL::HMAC.digest(OpenSSL::Digest.new("sha256"), APP_SECRET, raw_body)

# Attacker replays it, spoofing the shop-domain header to target shop-b:
headers = {
  "x-shopify-topic" => "orders/create",
  "x-shopify-hmac-sha256" => Base64.encode64(hmac), # unchanged, still valid
  "x-shopify-shop-domain" => "shop-b.myshopify.com", # victim, spoofed
  "x-shopify-webhook-id" => "attacker-controlled",
  "x-shopify-api-version" => "2024-01",
}

request = ShopifyAPI::Webhooks::Request.new(raw_body: raw_body, headers: headers)
ShopifyAPI::Webhooks::Registry.process(request)
# => HmacValidator.validate(request) returns true, because it only checks raw_body's HMAC.
# The host app's handler receives WebhookMetadata(shop: "shop-b.myshopify.com", body: attacker's payload),
# believing it genuinely came from shop-b.
```

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L15-33)
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
```

**File:** lib/shopify_api/webhooks/request.rb (L35-43)
```ruby
      sig { override.returns(String) }
      def to_signable_string
        @raw_body
      end

      sig { returns(T::Hash[String, T.untyped]) }
      def parsed_body
        JSON.parse(@raw_body)
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
