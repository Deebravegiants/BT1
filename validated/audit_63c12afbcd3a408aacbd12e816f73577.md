## Analysis

Mapping the report's bug class ("identity/authorization check that doesn't bind all the material it should") to this gem, the strongest analog is in the webhook HMAC verification: the `shop` identity used to dispatch a webhook is **not** part of the HMAC-signed material.

### Root cause

`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw body: [1](#0-0) 

The shop identity is read from a header that is *not* included in that signable string: [2](#0-1) [3](#0-2) 

`Registry.process` validates only the HMAC over that signable string (i.e., only the body), then trusts `request.shop` unconditionally when dispatching to the app's handler: [4](#0-3) 

`HmacValidator.validate` recomputes `HMAC(api_secret_key, verifiable_query.to_signable_string)` and compares it to the received signature — again, over body bytes only, never the shop header: [5](#0-4) 

### The broken binding

The intended invariant is:
`HMAC-verified(shop, body) == shop the handler acts on`

What is actually implemented is:
`HMAC-verified(body) ≠ shop the handler acts on` (shop is taken from an unauthenticated header)

Because Shopify signs webhooks with the app's single `client_secret` (`api_secret_key`), which is identical across every shop that installs the app, any shop's legitimately-received webhook gives an attacker a valid `(body, hmac)` pair. Nothing in this gem ties that pair to the specific shop it was issued for.

### Exploit path

1. An unprivileged attacker installs the target app on their own (e.g. free dev/test) shop — no special privilege, access token, or leaked secret required.
2. The app receives a real webhook (e.g. `orders/create`) at its endpoint, with attacker-influenced body content (order fields the attacker controls) and a valid `x-shopify-hmac-sha256` computed with the app's `client_secret`.
3. Attacker replays the exact same `raw_body` and `hmac` header to the app's webhook endpoint, but swaps `x-shopify-shop-domain` to a victim shop's domain.
4. `HmacValidator.validate` still passes (it only checks the body), and `Registry.process` calls `handler.handle(data: WebhookMetadata.new(..., shop: request.shop, ...))` with `shop` set to the victim's domain — the app now processes attacker-controlled data under a different tenant's identity.

This is a cross-tenant identity-binding break reachable by any unprivileged actor able to install the app once, matching the report's underlying pattern (Aragon's voting contract failing to bind identity/weight correctly to the action being authorized), translated to this gem's webhook verification.

### Title
Webhook `shop` identity is not covered by the HMAC signature, allowing cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` signs only the raw body, while `shop` (and all other headers) are excluded from the HMAC computation but are still trusted by `Registry.process` to route webhook data to the app's handler as the tenant identity.

### Finding Description
`Request#to_signable_string` returns `@raw_body` exclusively [6](#0-5) , so `Utils::HmacValidator.validate` only proves the body bytes were produced with knowledge of `api_secret_key`; it proves nothing about which shop the request is for. `Registry.process` nonetheless uses `request.shop`, read directly from the unauthenticated `x-shopify-shop-domain`/`shopify-shop-domain` header [2](#0-1) , as the trusted tenant identity passed to the app's registered handler [4](#0-3) . Since Shopify signs webhooks for all shops of an app with the same `client_secret`, a `(body, hmac)` pair obtained from one shop's genuine webhook remains valid when replayed with a different `shop` header value.

### Impact Explanation
This breaks the tenant boundary the HMAC is supposed to enforce: an attacker who can trigger any webhook against a shop they control can then replay that exact payload to the app with a spoofed `shop` header naming a victim tenant. The app's business logic (which trusts `WebhookMetadata#shop`) will act as though the event came from the victim shop — this is cross-tenant access/data injection, which is rated Critical impact.

### Likelihood Explanation
High reachability: no access token, `client_secret` value, or privileged account is needed by the attacker — only the ability to install the target app once on a shop they control (a normal, unprivileged action) to harvest a valid signed body, and the ability to send an HTTP request directly to the app's public webhook endpoint with a modified header.

### Recommendation
Include the shop domain (and ideally topic/webhook-id) inside the HMAC-signed material, or otherwise cryptographically bind them to the signature (e.g., sign a canonicalized string of `shop|topic|body` rather than `body` alone), and reject requests where the header-derived shop is not part of the verified signature.

### Proof of Concept
```ruby
# 1. Attacker installs the app on shop "attacker.myshopify.com" and triggers
#    a real webhook (e.g. orders/create). They capture the raw body and the
#    valid x-shopify-hmac-sha256 header Shopify sent, both signed with the
#    app's single, shop-agnostic client_secret.

raw_body = captured_body            # attacker-influenced order JSON
valid_hmac = captured_hmac_header   # HMAC(client_secret, raw_body)

# 2. Attacker POSTs directly to the app's webhook controller, replaying the
#    same body/hmac, but with the shop header swapped to the victim shop.
headers = {
  "x-shopify-topic" => "orders/create",
  "x-shopify-hmac-sha256" => valid_hmac,
  "x-shopify-shop-domain" => "victim-shop.myshopify.com", # spoofed
}

request = ShopifyAPI::Webhooks::Request.new(raw_body: raw_body, headers: headers)
ShopifyAPI::Webhooks::Registry.process(request)
# HmacValidator.validate(request) passes (only checks raw_body),
# handler.handle receives shop: "victim-shop.myshopify.com" -- cross-tenant spoof succeeds.
```

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

**File:** lib/shopify_api/webhooks/request.rb (L67-70)
```ruby
      sig { params(name: String).returns(T.untyped) }
      def shopify_header(name)
        @headers["shopify-#{name}"] || @headers["x-shopify-#{name}"]
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
