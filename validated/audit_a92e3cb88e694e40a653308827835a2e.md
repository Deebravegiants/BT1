### Title
Webhook tenant identity (`shop`) is not covered by the HMAC signature, allowing cross-tenant impersonation via header substitution - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request` derives the tenant-identifying `shop` (and `topic`) strictly from unauthenticated HTTP headers, while the HMAC signature verified by `ShopifyAPI::Utils::HmacValidator` covers only the raw request body. `ShopifyAPI::Webhooks::Registry.process` trusts `request.shop` after only confirming the *body* HMAC is valid, breaking the binding `hmac_signed_bytes == identity_bytes_acted_on`.

### Finding Description
`Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`Request#shop` and `Request#topic` are read straight from the `shopify-shop-domain`/`x-shopify-shop-domain` and `shopify-topic`/`x-shopify-topic` headers, which are never part of the signable string: [2](#0-1) 

`HmacValidator.validate` computes the HMAC over `to_signable_string` (the body only) and compares it to `verifiable_query.hmac`: [3](#0-2) 

`Registry.process` checks only this body-bound HMAC, then immediately uses the unauthenticated `request.shop` value to build the `WebhookMetadata` passed to the app's handler: [4](#0-3) 

Because `shop` is not part of the signed bytes, the equality the library relies on — `hmac_valid(body) == shop_is_authentic` — does not hold. Any request whose body matches one Shopify has previously signed (e.g., a webhook the attacker legitimately received for their own installed shop) still passes HMAC validation regardless of which `shop-domain` header value is sent, since only the body bytes are checked.

### Impact Explanation
An unprivileged internet user who is a legitimate merchant/installer of the app (and therefore receives real, validly-signed webhook deliveries for their own shop) can capture one such HTTP request and replay it to the app's public webhook endpoint with the `x-shopify-shop-domain` (or `shopify-shop-domain`) header changed to an arbitrary victim shop domain. The HMAC check still succeeds because it only verifies the body, and `Registry.process` will invoke the app's webhook handler with `shop: <attacker-chosen victim shop>`. Any app logic keyed on `WebhookMetadata#shop` (e.g., updating per-tenant records, triggering data exports, honoring `customers/redact` or `shop/redact` compliance webhooks) can be tricked into acting against the wrong tenant — a cross-tenant access/write vulnerability that fits the Critical impact category (cross-tenant access) defined in scope.

### Likelihood Explanation
Moderate-to-high. Exploitation requires only: (1) the attacker be able to install the app on any shop they control (a completely unprivileged, self-service action for most Shopify apps) to obtain one legitimately signed webhook body/HMAC pair, and (2) the ability to send an arbitrary HTTP request to the app's public webhook endpoint with a modified header — no access token, `client_secret`, or `api_secret_key` is needed, and no TLS interception or social engineering is required. The only constraint is that the victim's data of interest be reproducible in a body the attacker can obtain a valid signature for, or that the attacker replay a broad-topic webhook (e.g., `app/uninstalled`, `shop/update`) whose body content is not tenant-specific enough to matter, further raising likelihood for those topics.

### Recommendation
Bind the identity fields to the HMAC-verified data instead of trusting headers directly:
- Include `shop-domain`/`topic`/`webhook-id`/`api-version` header values in the signable string alongside the raw body (Shopify does not currently sign headers on the wire, so the safer fix is architectural): after validating the body HMAC, cross-check `request.shop` against an independently known, previously-registered/authenticated shop (e.g., the shop associated with the webhook subscription id via a server-side lookup, or the shop tied to the active offline session) rather than trusting the header value implicitly for any authorization decision.
- At minimum, document/enforce that `WebhookMetadata#shop` must never be used as the sole tenant identifier for privileged or destructive actions without a secondary authenticated lookup (e.g., verifying the shop has an active, previously stored session/access token), closing the gap between "HMAC-verified bytes" and "bytes acted upon."

### Proof of Concept
1. Attacker installs the target app on their own shop `attacker.myshopify.com`, triggering a real webhook delivery, e.g. for `customers/data_request`, with headers:
   - `x-shopify-hmac-sha256: <valid HMAC over the exact raw body>`
   - `x-shopify-shop-domain: attacker.myshopify.com`
   - `x-shopify-topic: customers/data_request`
2. Attacker captures this raw HTTP request (body + `hmac-sha256` header) verbatim.
3. Attacker resends the identical request to the app's webhook endpoint but changes only:
   - `x-shopify-shop-domain: victim-shop.myshopify.com`
4. Server-side, `ShopifyAPI::Webhooks::Request.new(raw_body:, headers:)` parses `shop` as `"victim-shop.myshopify.com"`.
5. `ShopifyAPI::Webhooks::Registry.process(request)` calls `Utils::HmacValidator.validate(request)` — this succeeds because `to_signable_string` is unchanged (same raw body), per: [5](#0-4) 
6. The app's registered handler is invoked with `WebhookMetadata.new(topic: ..., shop: "victim-shop.myshopify.com", body: ..., ...)`, causing the app to process/act as though the (attacker-crafted) data belongs to `victim-shop.myshopify.com`.

Note: I was unable to find any additional in-gem mitigation (e.g., a shop-domain check tied to a stored session or subscription id) inside `lib/shopify_api/webhooks/**`, and the `docs/usage/webhooks.md` guidance does not instruct implementers to cross-validate `shop` against anything beyond the HMAC-checked body — confirming this binding gap is not otherwise closed within the reviewed library scope.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L15-23)
```ruby
      sig { returns(String) }
      def topic
        T.cast(shopify_header("topic"), String)
      end

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
