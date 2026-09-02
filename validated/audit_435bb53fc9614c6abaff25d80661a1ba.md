### Title
Webhook shop-domain header is not covered by the HMAC signature, enabling cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw request body, while the `shop` (and `topic`, `api_version`, `webhook_id`) values are read directly from HTTP headers that are never included in the HMAC-signed material. `Registry.process` trusts `request.shop` to build the `WebhookMetadata` passed to the host app's handler after only validating the body's HMAC. This breaks the identity binding "shop authenticated == shop acted on," analogous to the ERC20 report's core defect where a value used to update contract state is not covered by the check that is supposed to guarantee its integrity.

### Finding Description
`Webhooks::Request` implements `Utils::VerifiableQuery`, whose contract only requires `hmac` and `to_signable_string`: [1](#0-0) 

The concrete implementation signs **only the raw body**: [2](#0-1) 

But `shop` (and `topic`) are pulled straight from attacker/Shopify-controlled headers, with no cryptographic linkage to the signature: [3](#0-2) 

`HmacValidator.validate` only recomputes the signature over `to_signable_string` (the body) and compares it to the `hmac` header — it never touches `shop`: [4](#0-3) 

`Registry.process` accepts the request once the (body-only) HMAC passes, and then forwards the **unverified** `request.shop` value to the app's webhook handler as the tenant identifier: [5](#0-4) 

Because the HMAC secret (`api_secret_key`) is the app's single client secret shared across every shop that has the app installed, any unprivileged internet user who installs the app on their own store can generate a validly-signed webhook (e.g. `orders/create`) for their own shop, capture the body + valid `x-shopify-hmac-sha256`, and then replay that exact request to the app's webhook endpoint while substituting `x-shopify-shop-domain` with a victim shop's domain. The signature check still passes (it only covers the body), but the handler receives `WebhookMetadata` claiming the event belongs to the victim shop. Equality broken: `shop authenticated by HMAC (∅, body only)` ≠ `shop used as the tenant key to route/store data`.

### Impact Explanation
This is a cross-tenant identity confusion: an attacker-controlled shop can forge webhook events that the host application will process as if they originated from another merchant's shop. Depending on how the host app's webhook handler uses `WebhookMetadata#shop` (e.g., to look up/update per-shop records, trigger per-shop side effects, or write into a shop-scoped data store), this can lead to cross-tenant data corruption or disclosure — squarely within the "Critical - cross-tenant access" impact category, since the attacker needs no privileged credential, only their own (attacker-owned) shop installation of the target app.

### Likelihood Explanation
Any user can install a public/embeddable app on a shop they control and legitimately trigger a webhook (e.g., by creating an order), giving them a fully valid `(body, hmac)` pair signed with the app's shared secret. Forging the `x-shopify-shop-domain` header on the replayed HTTP request requires no special access — it is a standard HTTP client capability. No access token, TLS interception, or social engineering is required, making this practically reachable by any unprivileged internet user who can install the target app once.

### Recommendation
Bind the `shop` (and ideally `topic`) value into the value that is actually verified, or otherwise cryptographically tie the shop domain to the signed payload — e.g., verify the shop domain against a known/installed-shop list before trusting `request.shop`, or require the host app to independently correlate the shop from a securely-stored session token rather than the raw header. At minimum, document that `Webhooks::Request#shop` is unauthenticated header data and must not be used as a sole tenant key without additional verification (e.g., cross-check against an existing offline session for that shop).

### Proof of Concept
1. Attacker installs the target Shopify app on their own store `attacker.myshopify.com`.
2. Attacker triggers a real webhook (e.g. `orders/create`) and captures the exact raw body `B` and the resulting valid header `x-shopify-hmac-sha256: H`, where `H = HMAC-SHA256(api_secret_key, B)`.
3. Attacker sends the identical body `B` and header `H` to the app's webhook endpoint, but sets `x-shopify-shop-domain: victim-shop.myshopify.com`.
4. `HmacValidator.validate` recomputes HMAC over `B` only (`Request#to_signable_string` returns `@raw_body`), matches `H`, and passes: [6](#0-5) 
5. `Registry.process` invokes the app's handler with `WebhookMetadata` whose `shop` is `"victim-shop.myshopify.com"`, even though the body/content actually originated from the attacker's own shop: [7](#0-6) 
6. Any host-app logic keyed on `data.shop` now operates against the victim tenant using attacker-supplied data.

### Citations

**File:** lib/shopify_api/utils/verifiable_query.rb (L10-16)
```ruby

      sig { abstract.returns(T.nilable(String)) }
      def hmac; end

      sig { abstract.returns(String) }
      def to_signable_string; end
    end
```

**File:** lib/shopify_api/webhooks/request.rb (L15-38)
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
