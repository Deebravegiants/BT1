### Title
Webhook `shop-domain` header is not covered by the HMAC signature, allowing cross-tenant shop spoofing in `Webhooks::Registry.process` - (File: `lib/shopify_api/webhooks/request.rb`, `lib/shopify_api/webhooks/registry.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates a webhook by validating an HMAC that is computed **only over the raw request body**, then hands the caller-supplied `shop-domain` header to the app as trusted tenant identity, without that header ever being bound to the HMAC. This breaks the identity binding `hmac_signed_bytes == bytes_that_determine_shop`, letting an unprivileged internet user replay a legitimately-signed webhook body with a forged `shop-domain` header to make the gem report an arbitrary victim shop.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw body: [1](#0-0) 

but `shop` (and `topic`, `webhook_id`, `api_version`) are read straight from unauthenticated headers, independent of that signed payload: [2](#0-1) 

`Registry.process` validates the HMAC via `Utils::HmacValidator.validate(request)`, which only checks `request.to_signable_string` (i.e. the body) against the secret: [3](#0-2) 

and once that body-only check passes, `Registry.process` immediately trusts `request.shop` and forwards it to the app's handler as the tenant identity, with no cross-check against anything the HMAC actually covers: [4](#0-3) 

The equality the gem should enforce is `hmac_signed_bytes ⊇ shop_identity_used`, but instead it holds `hmac_signed_bytes == body_only` while `shop_identity_used == unauthenticated_header`. Because the `shop-domain` header sits entirely outside the signed material, any two values `(body, hmac)` that are valid for one shop's webhook remain valid regardless of which `shop-domain` header accompanies them.

### Impact Explanation
An attacker who operates their own (even free/dev) Shopify store with the target app installed can trigger a legitimate webhook delivery to obtain one valid `(body, hmac)` pair for a topic the app handles. They can then POST that same body and HMAC directly to the app's public webhook endpoint while substituting an arbitrary victim `shop-domain` header. `Registry.process` will pass HMAC validation and invoke the app's handler with `WebhookMetadata#shop` set to the attacker-chosen victim shop, even though the payload never originated from that shop. Any host application that relies on `WebhookMetadata#shop` (as documented/intended) to key session lookups, tenant-scoped data writes, or webhook idempotency uses the gem's own untrusted value as a tenant identifier — leading to cross-tenant data confusion/corruption, which maps to the Critical "cross-tenant access" category.

### Likelihood Explanation
The webhook endpoint is by design a public, unauthenticated HTTP endpoint that must accept POSTs purportedly "from Shopify." Obtaining one valid `(body, hmac)` pair only requires installing the app on any shop the attacker controls and receiving one webhook of the relevant topic — no privileged credentials, secrets, or victim access is required. Replaying the pair with a different `shop-domain` header is a trivial HTTP-level manipulation.

### Recommendation
Bind the shop (and ideally topic/webhook id) into the signed material that is verified, or otherwise cryptographically tie the header-derived tenant identity to the HMAC-authenticated payload before it is trusted (e.g., include `shop`, `topic` in `to_signable_string`, or require the caller to separately verify the shop against a previously-established relationship/session before acting on `WebhookMetadata#shop`). At minimum, the gem should not silently pass an unauthenticated `shop` value through `Registry.process` after only validating the body's HMAC — the API surface should make clear that `shop` is unauthenticated unless additionally checked.

### Proof of Concept
```ruby
# Attacker owns their-shop.myshopify.com with the app installed and topic "orders/create" registered.
# Step 1: attacker receives a real webhook, capturing body + valid HMAC:
real_body = '{"id":1}'
real_hmac = Base64.encode64(
  OpenSSL::HMAC.digest(OpenSSL::Digest.new("sha256"), ShopifyAPI::Context.api_secret_key, real_body)
)

# Step 2: attacker replays the same (body, hmac) pair to the app's public webhook endpoint,
# but swaps the shop-domain header to the victim's shop:
forged_headers = {
  "x-shopify-topic" => "orders/create",
  "x-shopify-hmac-sha256" => real_hmac,
  "x-shopify-shop-domain" => "victim-shop.myshopify.com", # attacker-controlled, unauthenticated
}

request = ShopifyAPI::Webhooks::Request.new(raw_body: real_body, headers: forged_headers)
ShopifyAPI::Webhooks::Registry.process(request)
# => HMAC validation passes (only checks real_body against the shared secret),
#    and the handler is invoked with shop: "victim-shop.myshopify.com",
#    even though the payload never came from that shop.
```

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
