### Title
Webhook shop identity is not bound to the HMAC signature, enabling cross-tenant shop spoofing - (File: `lib/shopify_api/webhooks/request.rb`, `lib/shopify_api/webhooks/registry.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` treats a webhook as authentic for a given shop as long as `Utils::HmacValidator.validate(request)` passes, but the HMAC only covers the raw request body — never the `shop-domain` (or `topic`/`webhook-id`) header that the handler is actually given as the tenant identifier.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`#shop` is read straight from the `shopify-shop-domain`/`x-shopify-shop-domain` header, entirely outside the signed material: [2](#0-1) 

`HmacValidator.validate_signature` re-computes the HMAC over `verifiable_query.to_signable_string` (the body only) and compares it to the `hmac` header: [3](#0-2) 

`Registry.process` gates entirely on this body-only HMAC check, then forwards `request.shop` — unauthenticated — straight into `WebhookMetadata` that the application handler consumes as the tenant identity: [4](#0-3) 

The binding the library implies but does not enforce is:
`shop used to authorize the HMAC == shop the handler is told the payload came from`

In reality the equality only holds for:
`HMAC(secret, raw_body) == received_hmac`

`shop`, `topic`, `webhook_id`, and `api_version` are never part of that equation. Anyone who can obtain one legitimately-signed webhook body/HMAC pair for their **own** store (e.g., an attacker who installs the app on their own low-privilege store and receives real webhooks from Shopify) can replay that exact body+HMAC to the app's webhook endpoint while substituting a different `x-shopify-shop-domain` header value. `HmacValidator.validate` still returns `true` because it never inspects the header, and `Registry.process` will invoke the handler with `WebhookMetadata#shop` set to the attacker-chosen shop.

### Impact Explanation
Any application built on this gem that trusts `WebhookMetadata#shop` (the documented, expected way to identify which merchant a webhook belongs to) to select which tenant's data to read, write, or delete is exposed to cross-tenant data corruption/disclosure: an attacker-controlled shop identifier accompanies a body whose only guarantee is "was signed by the app's own secret for some body", not "for this particular shop". This meets the Critical bar of cross-tenant access, since the shop-identity binding that gates per-tenant state can be forged by any unprivileged actor who can trigger one genuine webhook to themselves.

### Likelihood Explanation
Exploitation only requires:
1. Installing the target app on an attacker-owned/free development store (a normal, unprivileged action), to legitimately receive at least one real, correctly-signed webhook (body + `hmac-sha256`).
2. Replaying that exact raw body and HMAC header to the app's public webhook endpoint with a forged `x-shopify-shop-domain` header for the victim shop.

No access to `api_secret_key`, tokens, or the victim's credentials is required, making this readily reachable by any internet user who can install the target app once.

### Recommendation
Include the shop domain (and ideally topic/webhook-id) in the HMAC-signable material, or independently verify that `request.shop` corresponds to a shop with a currently valid, stored session/access token before trusting it as the payload's origin, rather than relying on `HmacValidator.validate` alone to authenticate the header-derived `shop`.

### Proof of Concept
```ruby
# Attacker installs the app on their own shop "attacker.myshopify.com" and receives
# one real webhook whose body is "{}" — Shopify computes the HMAC over just the body:
hmac = OpenSSL::HMAC.digest(OpenSSL::Digest.new("sha256"), ShopifyAPI::Context.api_secret_key, "{}")

# Attacker now replays the same body+hmac but swaps the shop-domain header to the victim's shop:
forged_headers = {
  "x-shopify-topic"          => "orders/create",
  "x-shopify-hmac-sha256"    => Base64.encode64(hmac),   # still valid: HMAC never covered shop
  "x-shopify-shop-domain"    => "victim-shop.myshopify.com",
  "x-shopify-webhook-id"     => "attacker-controlled-id",
  "x-shopify-api-version"    => "2024-01",
}

forged_request = ShopifyAPI::Webhooks::Request.new(raw_body: "{}", headers: forged_headers)

# Passes validation despite the shop header being forged:
ShopifyAPI::Webhooks::Registry.process(forged_request)
# => handler.handle(data: WebhookMetadata.new(shop: "victim-shop.myshopify.com", ...))
```
The handler now believes the payload originated from `victim-shop.myshopify.com`, even though only the attacker's shop ever produced a genuinely signed body.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L20-23)
```ruby
      sig { returns(String) }
      def shop
        T.cast(shopify_header("shop-domain"), String)
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

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
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
