### Title
Webhook `shop` domain identity is not covered by the HMAC signature, allowing cross-tenant webhook spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` derives the tenant identity (`shop`) that is handed to the app's webhook handler from the unsigned `shopify-shop-domain` HTTP header, while the HMAC that `Webhooks::Registry.process` verifies only covers the raw request body. This breaks the identity binding `hmac_signed_bytes == bytes_the_handler_trusts_for_tenant_identity`, letting anyone who possesses one valid `(body, hmac)` pair replay it with an arbitrary `shop` header and have it accepted as coming from a different tenant.

### Finding Description
`Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`Webhooks::Request#shop` is read straight from the `shopify-shop-domain` / `x-shopify-shop-domain` header, which is not part of the signed bytes: [2](#0-1) 

`Utils::HmacValidator.validate` verifies the HMAC purely against `to_signable_string`, i.e., the body: [3](#0-2) 

`Registry.process` checks `HmacValidator.validate(request)` and then, on success, blindly forwards `request.shop` (the unverified header) to the app's registered handler as the tenant identity for that webhook payload: [4](#0-3) 

Because the `shop` header is never mixed into the HMAC-signed payload, `validate_signature` only proves "this body was signed with our secret" — it proves nothing about which shop the body is associated with. Any party who has captured one legitimately-signed `(raw_body, hmac)` pair (e.g., by installing the app on their own store and receiving their own webhooks) can resend that exact body/hmac pair to the app's webhook endpoint with the `shopify-shop-domain` header set to an arbitrary victim shop. `HmacValidator.validate` still returns `true` (the body/hmac match), and `Registry.process` calls the handler with `WebhookMetadata#shop` set to the attacker-chosen victim domain, while `body` is fully attacker-controlled (their own shop's payload).

### Impact Explanation
This is a cross-tenant identity binding break: the equality that should hold is `hmac_covers(shop) == true`, but in reality `hmac_covers(shop) == false`. Any app built on this gem that uses the `shop` field from `WebhookMetadata`/`Webhooks::Request` to key per-tenant data (order updates, uninstall/redact handling, billing state, GDPR compliance triggers, etc.) can be made to process attacker-supplied payloads under a victim shop's identity, since the HMAC check gives no assurance that the payload actually originated from that shop. This satisfies the Critical bar of "cross-tenant access" via a credential/binding the app relies on (the webhook HMAC) that this gem's `Request`/`Registry` implementation does not actually bind to shop identity.

### Likelihood Explanation
Any actor with a Shopify Partner account can install a target app on a shop they control and legitimately receive at least one valid `(raw_body, hmac)` webhook pair signed with the app's real secret (no `client_secret`/access-token theft required — this uses only their own store's traffic). They then only need to be able to send an HTTP request to the app's public webhook endpoint with a modified `shopify-shop-domain` header, which is trivial (curl/replay). No privileged account access or credential leakage is required — only the ability to install the app once and replay one captured request.

### Recommendation
Bind the tenant identity into the verified bytes rather than trusting an unauthenticated header:
- Include the `shop` domain (and ideally topic/webhook id) as part of the HMAC-signable payload construction in `Webhooks::Request#to_signable_string`, or
- Have `Registry.process` cross-check the `shop`/`topic` values embedded in the JSON body (if Shopify includes shop identifying fields there) against the header before dispatching to the handler, and document that consuming apps must not treat `shopify-shop-domain` as authenticated by the HMAC alone unless it is cryptographically bound.
At minimum, the gem should not silently forward the unauthenticated `shop` header as a "verified" tenant identity in `WebhookMetadata` without a clear disclaimer, since `HmacValidator.validate` gives callers no such guarantee today.

### Proof of Concept
```ruby
# Attacker installs the app on their own shop "attacker.myshopify.com" and captures
# one legitimately-signed webhook body+hmac (raw_body, hmac) — no secrets needed,
# just their own store's outgoing webhook traffic.

raw_body = '{"id":123,"note":"legit payload from attacker shop"}'
hmac = OpenSSL::HMAC.digest(OpenSSL::Digest.new("sha256"), ShopifyAPI::Context.api_secret_key, raw_body)

# Replay the SAME body/hmac, but claim it is from the victim shop:
spoofed_headers = {
  "shopify-topic" => "orders/updated",
  "shopify-hmac-sha256" => Base64.encode64(hmac),
  "shopify-shop-domain" => "victim-shop.myshopify.com", # <-- unauthenticated, attacker-controlled
  "shopify-webhook-id" => "whatever",
  "shopify-api-version" => "2024-01",
}

request = ShopifyAPI::Webhooks::Request.new(raw_body: raw_body, headers: spoofed_headers)

ShopifyAPI::Utils::HmacValidator.validate(request) # => true, because HMAC only covers raw_body

ShopifyAPI::Webhooks::Registry.process(request)
# The registered handler receives WebhookMetadata(shop: "victim-shop.myshopify.com", body: attacker's JSON, ...)
# even though the payload never originated from victim-shop.myshopify.com.
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
