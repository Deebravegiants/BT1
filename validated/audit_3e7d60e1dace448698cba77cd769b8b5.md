### Title
Webhook `shop` (and `topic`/`webhook_id`) header is not covered by HMAC, allowing cross-tenant webhook spoofing/replay - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request` derives the tenant identity (`shop`) from an unauthenticated HTTP header, while `Utils::HmacValidator` only verifies the HMAC over the raw request body. Because the signed content never includes the shop identifier, a party who possesses one genuinely-signed webhook (e.g. from their own store's installation of the app) can replay that exact body+HMAC pair while substituting the `shop-domain` header to name a different (victim) shop, and the signature check will still pass.

### Finding Description
`Request#to_signable_string` returns only the raw body: [1](#0-0) 

`HmacValidator.validate_signature` computes and compares the HMAC exclusively over that signable string: [2](#0-1) 

The `shop`, `topic`, `api_version`, and `webhook_id` fields are read straight from headers with no cryptographic binding to the body or to each other: [3](#0-2) 

`Registry.process` validates only the HMAC and then forwards the unauthenticated `request.shop` directly to the app's handler as trusted tenant metadata: [4](#0-3) 

Because the app's `client_secret`/`api_secret_key` is shared across every shop that installs the app (it is not per-shop), any merchant who installs the app on their own store legitimately receives HMAC-valid webhook deliveries signed with that same shared secret. Since the signature covers only the body bytes and not the `shop-domain` header, that same signed body can be replayed against the app's webhook endpoint with the `shop-domain` header changed to a victim shop. `Utils::HmacValidator.validate` will still return `true` because it only re-computes `HMAC(secret, raw_body)` and compares it — it never checks that the body was actually produced for the shop named in the header.

This breaks the intended identity binding: the equality the code should enforce is `hmac_signed_shop == header_shop`, but the actual check performed is only `hmac(body) == received_hmac`, with `header_shop` never entering the signed material.

### Impact Explanation
This is a cross-tenant confusion vector: a handler that trusts `WebhookMetadata#shop` (as `Registry.process` explicitly does when constructing it from `request.shop`) can be made to process attacker-supplied body content under a victim shop's identity, since the shop attribution is unauthenticated. Depending on how the host app uses `data.shop` (e.g., to look up the shop's session/access token and act on its behalf, or to write shop-scoped records), this can lead to cross-tenant data corruption or actions being taken against the wrong tenant — a Critical-tier cross-tenant access issue per the impact classes in scope.

### Likelihood Explanation
The prerequisite is modest: the attacker only needs to install the target app on any shop they control (a routine, unprivileged action available to any Shopify merchant) to obtain a genuinely HMAC-signed webhook body, then replay it toward the app's public webhook endpoint with a substituted `x-shopify-shop-domain`/`shopify-shop-domain` header. No access token, `api_secret_key`, or privileged credential is required — only the interaction the gem itself performs (`Utils::HmacValidator.validate` checking body bytes only).

### Recommendation
Bind the tenant identity into the verified material, or otherwise cryptographically tie the `shop` header to the signed body — e.g., include `shop-domain` (and `topic`, `webhook-id`) in the HMAC-signed string in `Request#to_signable_string`, or have `HmacValidator.validate` take the full header set as part of the signable content instead of the body alone. Document for host apps that `WebhookMetadata#shop` should not be treated as an authenticated tenant claim unless this binding is added.

### Proof of Concept
1. Install the target Shopify app on attacker-controlled shop `attacker.myshopify.com`; capture a real webhook delivery, e.g. `orders/create`, with headers:
   - `x-shopify-hmac-sha256: <valid HMAC of raw body under app's shared secret>`
   - `x-shopify-shop-domain: attacker.myshopify.com`
   - raw body `B`
2. Replay the exact same raw body `B` and the exact same `x-shopify-hmac-sha256` value to the app's webhook endpoint, but change the header to `x-shopify-shop-domain: victim.myshopify.com`.
3. Trace through `ShopifyAPI::Webhooks::Request.new` → `Utils::HmacValidator.validate` (`lib/shopify_api/utils/hmac_validator.rb:13-22`): validation succeeds because it only recomputes `HMAC(secret, B)`, which is unchanged.
4. `Registry.process` (`lib/shopify_api/webhooks/registry.rb:188-200`) invokes the handler with `WebhookMetadata.new(..., shop: "victim.myshopify.com", body: parsed(B), ...)`, i.e. attacker-controlled body content now attributed to the victim shop.

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
