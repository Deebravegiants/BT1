### Title
Webhook `shop`, `topic`, and `webhook-id` are trusted from unauthenticated headers while the HMAC only covers the raw body, enabling cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw request body, so the HMAC signature computed by `Utils::HmacValidator` binds *only* the payload bytes to the app's `client_secret`. The `shop-domain`, `topic`, and `webhook-id` HTTP headers are parsed and exposed via `Request#shop`, `#topic`, and `#webhook_id` but are never included in the signed material. `Webhooks::Registry.process` validates the HMAC and then forwards `request.shop` (an unauthenticated header value) straight into `WebhookMetadata`, which host applications use to identify the tenant the event belongs to.

### Finding Description
The identity binding that should hold is:
`shop authenticated by HMAC == shop acted upon by the handler`

In practice:
- `Utils::HmacValidator.validate` computes `HMAC(secret, verifiable_query.to_signable_string)` and compares it to the `hmac` header [1](#0-0) .
- For webhooks, `to_signable_string` returns only `@raw_body`, never the `shop-domain`, `topic`, or `webhook-id` headers [2](#0-1) .
- `Registry.process` validates the HMAC and then blindly trusts `request.shop`, `request.topic`, and `request.webhook_id` — none of which were covered by the signature — to build `WebhookMetadata` that the app's handler acts on [3](#0-2) .

Because the app's `client_secret` (and therefore the HMAC key) is shared across *all* shops that install the app, any shop that legitimately receives a webhook obtains a valid `(body, hmac)` pair signed under that shared secret. That pair remains valid HMAC-wise regardless of which `shop-domain` header accompanies it, since the header is excluded from the signed string. An attacker who can reach the app's public webhook endpoint directly (bypassing Shopify's delivery infrastructure entirely — no interception or Shopify credentials required) can replay a previously observed `(body, hmac)` pair with an arbitrary `X-Shopify-Shop-Domain` header value, and `Registry.process` will accept it as authentic and dispatch it to the handler under the forged shop identity.

### Impact Explanation
This breaks the tenant-identity binding the HMAC is supposed to establish: `Registry.process` reports "HMAC valid" while the `shop` (and `topic`/`webhook_id`) actually driving application logic is unauthenticated attacker input. Host applications commonly use `WebhookMetadata#shop` to look up the merchant's session/access token or to key database writes (e.g., `app/uninstalled`, `orders/create`, `shop/redact`). An attacker can spoof events as coming from a shop they do not control, leading to cross-tenant data confusion — e.g., forging an `app/uninstalled` event for a victim shop to trigger token/data deletion, or injecting a crafted (但 still Shopify-shaped) payload under a victim's identity. This qualifies as cross-tenant access impact.

### Likelihood Explanation
Exploitation requires only: (1) knowledge/discovery of the app's public webhook endpoint URL (necessarily internet-reachable so Shopify can deliver to it), and (2) one legitimately observed `(raw_body, hmac)` pair — trivially obtainable by installing the app on any shop (even a free/dev store) and inspecting an incoming webhook. No access token, `client_secret`, or privileged account is required, satisfying the "unprivileged internet user" bar.

### Recommendation
Bind the header-derived identity fields into the signed material, or otherwise cryptographically tie `shop`, `topic`, and `webhook_id` to the HMAC before trusting them:
- If matching Shopify's actual wire format is not possible (Shopify only signs the body), have `Registry.process` treat `request.shop`/`topic`/`webhook_id` as untrusted metadata and require the host application to cross-check `request.shop` against an independently verified session/install record before acting, and document this requirement prominently.
- At minimum, add replay protection (e.g., reject re-processing of the same `webhook_id` value) so a captured `(body, hmac)` pair cannot be replayed under a different `shop-domain` header.

### Proof of Concept
1. Install the target app on attacker-controlled shop `attacker.myshopify.com`; capture a legitimately delivered webhook request, e.g. `orders/create`, along with its `X-Shopify-Hmac-Sha256` header and raw body.
2. Send a forged POST request directly to the app's public webhook endpoint (bypassing Shopify) with:
   - The same raw body and `X-Shopify-Hmac-Sha256` value captured in step 1.
   - `X-Shopify-Topic: app/uninstalled` (or another topic) and `X-Shopify-Shop-Domain: victim.myshopify.com`.
3. `Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which succeeds because it only checks `HMAC(secret, raw_body)` [4](#0-3) [5](#0-4) .
4. The handler receives `WebhookMetadata` with `shop: "victim.myshopify.com"` [6](#0-5) , and the host application acts on the victim shop's identity based entirely on attacker-controlled, unauthenticated header data.

### Citations

**File:** lib/shopify_api/utils/hmac_validator.rb (L12-22)
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

**File:** lib/shopify_api/webhooks/request.rb (L10-13)
```ruby
      sig { override.returns(String) }
      def hmac
        Digest.hexencode(Base64.decode64(T.cast(shopify_header("hmac-sha256"), String)))
      end
```

**File:** lib/shopify_api/webhooks/request.rb (L35-38)
```ruby
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
