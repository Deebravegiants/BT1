## Analysis

I found a valid analog matching the "field acted on but not covered by the HMAC" bug class from the rules.

### Title
Webhook shop/topic/webhook-id identity fields are not covered by the HMAC signature, enabling cross-tenant webhook impersonation - (`lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC over the raw request body only, while the `shop-domain`, `topic`, `webhook-id`, and `api-version` values are read straight from unauthenticated HTTP headers and later passed to the app's webhook handler as trusted identity data. Because these header fields are never part of the signed payload, an attacker who obtains one valid `(body, hmac)` pair — trivially available by installing the app on their own store and capturing one of their own real webhook deliveries — can replay that exact body/signature pair while substituting an arbitrary victim `shop-domain` header. `Utils::HmacValidator.validate` will still pass because it only checks the body bytes, and `Registry.process` will hand the forged shop identity to the handler as if it were authentic.

### Finding Description
`Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`Request#shop`, `#topic`, `#webhook_id`, and `#api_version` are all read directly from HTTP headers, none of which are included in `to_signable_string`: [2](#0-1) 

`Utils::HmacValidator.validate` computes and compares the signature solely against `to_signable_string` (the body), never the headers: [3](#0-2) 

`Registry.process` gates on this body-only HMAC check and then forwards the unauthenticated `request.shop`, `request.topic`, and `request.webhook_id` header values straight into `WebhookMetadata` passed to the app's handler: [4](#0-3) 

**Identity binding broken (as an equality):**
`shop_bytes_verified_by_HMAC == shop_bytes_used_by_handler` does **not** hold. The bytes cryptographically verified are `raw_body` only; the bytes acted upon for tenant routing (`shop-domain` header) are unauthenticated and attacker-controllable independently of the signed body.

**Attack sequence:**
1. Attacker installs the app on their own store (no privilege required — any merchant can install a public/dev app) and receives a legitimately signed webhook delivery: `(raw_body_A, hmac_A)` where `hmac_A = HMAC(client_secret, raw_body_A)`.
2. Attacker replays a crafted HTTP POST to the app's webhook endpoint with the identical `raw_body_A` and `x-shopify-hmac-sha256: hmac_A`, but sets `x-shopify-shop-domain: victim-shop.myshopify.com` (and optionally a different `x-shopify-topic`/`x-shopify-webhook-id`).
3. `HmacValidator.validate` succeeds because it only checks `raw_body_A` against `hmac_A` — headers are irrelevant to the check.
4. `Registry.process` looks up the handler by `request.topic` (attacker-controlled) and invokes it with `shop: request.shop` set to `victim-shop.myshopify.com` — a shop the attacker never installed on and has no relationship with.

Before the request: verified party = attacker's own shop (via legitimate install). After the forged replay: the handler believes the event originates from `victim-shop.myshopify.com`, a different tenant, with no additional check ever comparing the header-derived shop identity to anything cryptographically bound to the signature.

### Impact Explanation
This breaks the tenant boundary the HMAC check is meant to enforce. Any app that uses `request.shop` from `WebhookMetadata` to key data lookups, trigger uninstall/cleanup logic, update per-shop billing/subscription state, or otherwise act on behalf of "the shop that sent this webhook" can be manipulated into performing actions against an arbitrary victim shop, using only a webhook body the attacker legitimately received for their own store. This is cross-tenant access achieved without any credential belonging to the victim, matching the "Critical - cross-tenant access" impact category.

### Likelihood Explanation
Likelihood is high: obtaining a valid `(body, hmac)` pair requires nothing more than installing the app on any store the attacker controls (including a free development store), which is available to any unprivileged internet user. Forging headers on an HTTP request is trivial. No knowledge of `client_secret`, access tokens, or any victim credential is required.

### Recommendation
Bind the shop (and ideally topic/webhook_id) identity into the signed material, or independently verify it out-of-band: e.g., after HMAC validation succeeds, cross-check `request.shop` against a shop the app has an active session/installation for, and treat header-only fields as untrusted routing hints rather than authenticated identity. At minimum, document prominently that `shop`, `topic`, and `webhook_id` are not covered by the HMAC and must not be used for authorization decisions without an additional binding check (e.g., verifying an active stored session exists for that shop before trusting the payload as belonging to it).

### Proof of Concept
```ruby
require "openssl"
require "base64"

secret = ShopifyAPI::Context.api_secret_key
raw_body = '{"id":1,"note":"legit event from attacker_own_shop"}'
hmac = OpenSSL::HMAC.digest(OpenSSL::Digest.new("sha256"), secret, raw_body)

# Step 1: attacker legitimately receives this from Shopify for THEIR OWN store
legit_headers = {
  "x-shopify-topic" => "orders/create",
  "x-shopify-hmac-sha256" => Base64.encode64(hmac),
  "x-shopify-shop-domain" => "attacker-shop.myshopify.com",
  "x-shopify-webhook-id" => "attacker-webhook-id",
  "x-shopify-api-version" => "2024-01",
}

# Step 2: attacker replays the SAME body/hmac but swaps the shop-domain header
forged_headers = legit_headers.merge(
  "x-shopify-shop-domain" => "victim-shop.myshopify.com",
)

forged_request = ShopifyAPI::Webhooks::Request.new(raw_body: raw_body, headers: forged_headers)

# Passes because HMAC only ever validated raw_body, never the shop-domain header
ShopifyAPI::Utils::HmacValidator.validate(forged_request) # => true

# Registry.process will now hand off `shop: "victim-shop.myshopify.com"` to the
# app's handler, even though the attacker has no relationship with that shop.
ShopifyAPI::Webhooks::Registry.process(forged_request)
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

**File:** lib/shopify_api/webhooks/request.rb (L35-38)
```ruby
      sig { override.returns(String) }
      def to_signable_string
        @raw_body
      end
```

**File:** lib/shopify_api/utils/hmac_validator.rb (L12-40)
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

        sig { params(signable_string: String, secret: String).returns(String) }
        def compute_signature(signable_string, secret)
          OpenSSL::HMAC.hexdigest(
            OpenSSL::Digest.new("sha256"),
            secret,
            signable_string,
          )
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
