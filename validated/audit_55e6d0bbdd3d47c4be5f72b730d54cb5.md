### Title
Webhook `shop` (and `topic`) attribution is not covered by the HMAC signature, allowing cross-tenant spoofing of webhook origin - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an inbound webhook solely by validating the HMAC of the raw request body, then trusts the `shop-domain` header verbatim when constructing the `WebhookMetadata` passed to the app's handler. The HMAC never covers the `shop` field, so the binding "HMAC-verified request == request attributed to `shop`" does not hold.

### Finding Description
`Webhooks::Request#to_signable_string` returns only `@raw_body`, and `hmac` is read from the `hmac-sha256` header: [1](#0-0) [2](#0-1) 

`HmacValidator.validate` computes `HMAC(secret, to_signable_string)` and compares it to the received `hmac`, i.e. it only proves the body bytes were signed by someone holding `api_secret_key` - it says nothing about which shop the body belongs to: [3](#0-2) 

`Registry.process` uses this same validation and then forwards `request.shop` (parsed straight from the unauthenticated `shop-domain`/`x-shopify-shop-domain` header) to the handler as the authoritative tenant identity: [4](#0-3) [5](#0-4) 

Because `api_secret_key` is the single, app-wide secret shared across every merchant install (not a per-shop value verified against the header), any party who can obtain one valid `(raw_body, hmac)` pair signed with the app's secret — e.g., their own shop's legitimate webhook delivery — can replay that exact body/HMAC pair while substituting an arbitrary `shop-domain` header. `HmacValidator.validate` will still return `true` because it never inspects the `shop` field, and `Registry.process` will hand the handler a `WebhookMetadata` claiming the payload originated from the victim shop.

This breaks the intended identity binding: `hmac_valid(body) == request originated from shop`. In this gem, the correct binding should be `hmac_valid(body) && shop == expected_tenant`, but no such secondary check exists in the library, and the header used for `shop` attribution is completely outside the signed material.

### Impact Explanation
Any host application that relies on `WebhookMetadata#shop` (as returned by this gem) to select which merchant's data/session to act on — e.g., to look up that shop's offline session and perform writes, or to route mandatory GDPR webhooks (`shop/redact`, `customers/redact`, `customers/data_request`) — can be tricked into processing a payload under an attacker-chosen shop identity, since the gem provides no mechanism, field, or documented guard binding the HMAC-verified bytes to the shop header. This is a cross-tenant identity confusion at the library's trust boundary: the one signal (`HmacValidator.validate`) an app is expected to rely on for webhook authenticity provides no tenant binding at all.

### Likelihood Explanation
Exploitation requires the attacker to possess at least one valid `(body, hmac)` pair produced under the app's `api_secret_key` — realistically obtainable by operating their own legitimate install of the app (an unprivileged action any developer/merchant can perform) and capturing a webhook delivery to their own endpoint. From there, replaying the identical body/HMAC with a forged `shop-domain` header is trivial and entirely within an unprivileged internet user's capability; it requires no access to any other merchant's credentials, tokens, or secrets.

### Recommendation
Include the shop domain (and ideally topic/webhook-id) inside the HMAC-signed material, or require host applications to cross-check the `shop` value against a known/expected tenant (e.g., an existing session record) before trusting `WebhookMetadata#shop`. At minimum, document explicitly in `Webhooks::Registry.process` / `Webhooks::Request` that the `shop` and `topic` header values are unauthenticated and must be independently validated by the consuming application against its own tenant registry before being used for any privileged action.

### Proof of Concept
1. Attacker installs the target app on their own shop `attacker.myshopify.com` and registers/receives a legitimate webhook, capturing `raw_body = "{}"` and its valid `x-shopify-hmac-sha256` value (computed by Shopify with the app's real `api_secret_key`).
2. Attacker sends a new HTTP request to the app's webhook endpoint with the *same* `raw_body` and *same* `hmac` header, but sets `x-shopify-shop-domain: victim-shop.myshopify.com`.
3. The app calls `ShopifyAPI::Webhooks::Registry.process(request)`, which invokes `Utils::HmacValidator.validate(request)` — this passes because it only recomputes the HMAC over `raw_body`, per `lib/shopify_api/webhooks/request.rb:36-38` and `lib/shopify_api/utils/hmac_validator.rb:26-31`.
4. `Registry.process` builds `WebhookMetadata.new(topic: request.topic, shop: request.shop, ...)` using the forged `shop` value (`lib/shopify_api/webhooks/registry.rb:198-199`), and the registered handler runs believing the event came from `victim-shop.myshopify.com`.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L10-23)
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
```

**File:** lib/shopify_api/webhooks/request.rb (L35-38)
```ruby
      sig { override.returns(String) }
      def to_signable_string
        @raw_body
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
