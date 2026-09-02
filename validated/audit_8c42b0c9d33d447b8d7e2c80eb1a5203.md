### Title
Webhook `shop-domain` header is not covered by the HMAC signature, enabling cross-tenant webhook spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw request body, while the `shop` used downstream to attribute the webhook to a tenant comes from the unauthenticated `shop-domain` header. Because the HMAC only binds the body, an attacker who has one genuine `(body, hmac)` pair signed with the app's shared `api_secret_key` can replay it with a different `shop-domain` header and the signature check still passes, letting the payload be processed as if it came from a different merchant.

### Finding Description
`Webhooks::Request#to_signable_string` is defined to sign only `@raw_body`: [1](#0-0) 

`shop` is instead read straight from the `shopify-shop-domain`/`x-shopify-shop-domain` HTTP header, with no cryptographic tie to the signed content: [2](#0-1) 

`Registry.process` validates the HMAC over the request (i.e., only the body) and then builds `WebhookMetadata` using the unverified `request.shop`, which is handed directly to the app's registered handler: [3](#0-2) 

`HmacValidator.validate` computes the signature purely from `to_signable_string`, so it never sees or binds the `shop` header: [4](#0-3) 

Because every shop that installs the app shares the same `api_secret_key`, any tenant is able to legitimately trigger a real webhook to the app (e.g. `orders/create`, `app/uninstalled`) for its own store, capturing a genuinely-signed `(raw_body, hmac)` pair. That attacker-controlled tenant can then send its own crafted HTTP POST to the app's webhook endpoint reusing the captured body/HMAC but substituting the `x-shopify-shop-domain` header with a victim shop's domain. `HmacValidator.validate` still succeeds, because the header is not part of the signed content, and `Registry.process` dispatches the handler believing the event originated from the victim shop.

This breaks the intended identity binding:
`shop authenticated by HMAC` ⇔ `shop stored/acted upon by the handler`

In this gem, the HMAC covers only the body; the shop identity used for all downstream tenant-scoped actions is taken from an unauthenticated header.

### Impact Explanation
This is a cross-tenant access vulnerability (High/Critical class per the rules): a low-privileged attacker who is merely a legitimate merchant using the app can forge webhook events that the host application will process under a *different* tenant's identity. Depending on how the host app's webhook handler uses `WebhookMetadata#shop` (common patterns include looking up/mutating the corresponding tenant's stored session, marking a shop uninstalled, processing GDPR/compliance webhooks, or writing data keyed by shop), this can lead to unauthorized cross-tenant data manipulation, spoofed uninstall/reinstall events, or corruption of another merchant's stored session data — all without ever needing the app's `api_secret_key`, an access token, or any privileged credential.

### Likelihood Explanation
Likelihood is realistic: the attacker only needs to be an app-installing merchant (an "unprivileged internet user" from the app's perspective) capable of triggering one webhook event addressed to themselves (trivial, e.g. by creating an order or uninstalling/reinstalling the app), then replaying the same raw bytes with a different `shop-domain` header value against the public webhook endpoint. No secret material, TLS interception, or social engineering is required — only structural knowledge of this gem's HMAC scope (body-only).

### Recommendation
Bind the `shop` (and ideally `topic`/`webhook_id`) into the value that is HMAC-verified, or otherwise cryptographically tie the header-derived `shop` to the verified body (e.g., include it as part of the canonical signed string, or cross-check it against a shop already known/authorized for that specific installation/session rather than trusting the header verbatim). At minimum, document and enforce that `request.shop` must never be trusted for tenant attribution unless it is corroborated by the app's own installed-session lookup for that shop, not solely by a successful raw-body HMAC check.

### Proof of Concept
1. Attacker installs the target app on their own store `attacker.myshopify.com` and captures one legitimate webhook delivery, e.g. body `{"id":123}` and header `x-shopify-hmac-sha256: <valid-mac-of-body>` (this MAC was computed by Shopify using the shared `api_secret_key`, as in `HmacValidator.validate`/`compute_signature`) — [5](#0-4) .
2. Attacker sends a POST to the app's webhook endpoint with the exact same body/`hmac` header, but sets `x-shopify-shop-domain: victim.myshopify.com`.
3. `ShopifyAPI::Webhooks::Request.new` parses headers, and `Registry.process` calls `Utils::HmacValidator.validate(request)`, which succeeds because the signature only covers `raw_body` — [6](#0-5) .
4. The handler receives `WebhookMetadata` with `shop: "victim.myshopify.com"` and processes the event as if it were sent by the victim tenant — [7](#0-6) .

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L20-38)
```ruby
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

**File:** lib/shopify_api/utils/hmac_validator.rb (L33-40)
```ruby
        sig { params(signable_string: String, secret: String).returns(String) }
        def compute_signature(signable_string, secret)
          OpenSSL::HMAC.hexdigest(
            OpenSSL::Digest.new("sha256"),
            secret,
            signable_string,
          )
        end
```
