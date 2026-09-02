### Title
Webhook HMAC Signature Does Not Cover the `shop-domain`, `topic`, `webhook-id`, or `api-version` Headers, Enabling Cross-Tenant Webhook Spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` derives the shop, topic, webhook id, and API version that a webhook handler acts on from raw HTTP headers, but the HMAC signature that `Utils::HmacValidator.validate` checks only covers the raw request body. Because the identity of the tenant (`shop`) is never part of the signed material, a valid `(body, hmac)` pair produced for one shop can be replayed against the same endpoint with a forged `shop-domain` header naming a different shop, and the signature will still validate.

### Finding Description
`Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

Meanwhile `shop`, `topic`, `webhook_id`, and `api_version` are all pulled straight from HTTP headers, which are never part of the signed string: [2](#0-1) 

`Utils::HmacValidator.validate` computes the HMAC over `verifiable_query.to_signable_string` (the body only) and compares it to the `hmac-sha256` header: [3](#0-2) 

`Registry.process` trusts `request.topic` and `request.shop` directly after the HMAC check passes, and hands them to the handler as authenticated metadata: [4](#0-3) 

This is the same class of bug as the LP-fee analog: the value that downstream logic actually keys tenant/shop attribution on (`shop-domain` header) is a field that is "acted on" but not bound by the cryptographic check ("bytes verified" = raw body, "bytes parsed/acted on" = headers). Since one `client_secret` is shared by an app across every shop that installs it, any shop that installs the app can legitimately receive a validly-signed `(body, hmac)` pair from Shopify for its own store, then replay that exact pair to the app's public webhook endpoint while substituting the `shop-domain` (and optionally `topic`/`webhook-id`) header to point at a victim shop. The HMAC still validates because it never covered those headers, so the handler processes attacker-supplied webhook metadata as if it legitimately originated from the victim shop.

### Impact Explanation
This breaks the identity binding "shop authenticated == shop the webhook is attributed to." An attacker who is merely an installed (unprivileged) user of the app on their own store can forge webhook deliveries that the receiving application will treat as authentic events for an arbitrary other shop (cross-tenant access), e.g. triggering mandatory compliance webhooks (`shop/redact`, `customers/redact`), `app/uninstalled` handling, or business-logic webhooks against another merchant's session/data — all without ever possessing that shop's credentials.

### Likelihood Explanation
Any developer using this gem's webhook stack (`ShopifyAPI::Webhooks::Registry.process` / `Request`) as documented is affected; no misuse of the API is required. The attacker only needs to install the target app on a store they control (a normal, unprivileged action) to obtain one legitimately signed `(body, hmac)` pair, then replay it with modified headers to the shared, internet-reachable webhook endpoint.

### Recommendation
Include the tenant-identifying fields (`shop-domain`, and ideally `topic`/`webhook-id`) in the signed material verified against the HMAC, or otherwise cryptographically/contextually bind the header-derived `shop` to the session/webhook subscription the handler operates on (e.g., re-validate that the webhook id belongs to a subscription registered for the claimed shop) before trusting `WebhookMetadata#shop` for any tenant-scoped action.

### Proof of Concept
1. Attacker installs the target app on `attacker-shop.myshopify.com`. Shopify sends a legitimately signed webhook: body `B`, header `X-Shopify-Hmac-Sha256: H` (valid for `B` under the app's shared `client_secret`), and `X-Shopify-Shop-Domain: attacker-shop.myshopify.com`.
2. Attacker captures `(B, H)` and re-POSTs it to the same public webhook endpoint, keeping body `B` and header `H` unchanged but replacing `X-Shopify-Shop-Domain: victim-shop.myshopify.com`.
3. `Utils::HmacValidator.validate` recomputes HMAC over `B` only (`to_signable_string` = `@raw_body`) and it matches `H`, so validation passes (`lib/shopify_api/utils/hmac_validator.rb:12-31`, `lib/shopify_api/webhooks/request.rb:35-38`).
4. `Registry.process` dispatches the handler with `WebhookMetadata.new(shop: "victim-shop.myshopify.com", ...)` (`lib/shopify_api/webhooks/registry.rb:198-199`), so the host application processes attacker-controlled data as an authenticated event for `victim-shop.myshopify.com`.

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
